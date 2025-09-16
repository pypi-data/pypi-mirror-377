from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta

from flask import Blueprint, make_response, session
from sqlalchemy import func as sql_func

import ckan.lib.helpers as h
import ckan.model as model
import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan.logic import functools
from ckan.logic.action.create import _get_random_username_from_email

from ckanext.saml import config, utils
from ckanext.saml.interfaces import ICKANSAML
from ckanext.saml.model.user import User

log = logging.getLogger(__name__)
use_nameid_as_email = tk.asbool(tk.config.get("ckan.saml_use_nameid_as_email", False))

saml_details = [
    "samlUserdata",
    "samlNameIdFormat",
    "samlNameId",
    "samlCKANuser",
]

saml = Blueprint("saml", __name__)


@functools.lru_cache(1)
def get_bp():
    saml.add_url_rule(config.slo_path(), view_func=post_logout)

    saml.add_url_rule(config.sso_path(), view_func=post_login, methods=["POST"])

    return saml


def post_logout():
    if "SAMLResponse" in tk.request.args:
        log.debug(
            "SAML2 Logout response: %s",
            utils.decode_saml_response(tk.request.args["SAMLResponse"]),
        )
    return tk.h.redirect_to("user.logout")


def post_login():
    req = utils.prepare_from_flask_request()
    auth = utils.make_auth(req)

    request_id = None
    auth.process_response(request_id=request_id)
    errors = auth.get_errors()

    if errors:
        log.error("Cannot process IdP response: %s", errors)
        log.error("Last error reason: %s", auth.get_last_error_reason())

        error_tpl = config.error_template()
        if error_tpl:
            return tk.render(error_tpl, {"errors": errors})

        h.flash_error("Login failed.")
        return h.redirect_to(h.url_for("saml.saml_login"))

    log.debug("User succesfully logged in the IdP. Extracting NAMEID.")
    nameid = auth.get_nameid()

    if not nameid:
        log.error("Something went wrong, no NAMEID was found, redirecting back to to login page.")
        return h.redirect_to(h.url_for("user.login"))

    mapped_data = {}
    attr_mapper = tk.h.saml_attr_mapper()

    if not attr_mapper:
        log.error('User mapping is empty, please set "ckan.saml_custom_attr_map" param in config.')
        return h.redirect_to(h.url_for("user.login"))

    for key, value in attr_mapper.items():
        field = auth.get_attribute(value)
        if field:
            mapped_data[key] = field
    log.debug(f"NAMEID: {nameid}")

    for item in p.PluginImplementations(ICKANSAML):
        item.after_mapping(mapped_data, auth)
    log.debug("Client data: %s", attr_mapper)
    log.debug("Mapped data: %s", mapped_data)
    log.debug("If you are experiencing login issues, make sure that email is present in the mapped data")
    saml_user = model.Session.query(User).filter(User.name_id == nameid).first()

    if not saml_user:
        log.debug(f"No User with NAMEID '{nameid}' was found. Creating one.")

        try:
            email = nameid if config.use_nameid_as_email() else mapped_data["email"][0]

            log.debug(f'Check if User with "{email}" email already exists.')
            user_exist = (
                model.Session.query(model.User)
                .filter(sql_func.lower(model.User.email) == sql_func.lower(email))
                .first()
            )

            if user_exist:
                log.debug(f'Found User "{user_exist.name}" that has same email.')
                new_user = user_exist.as_dict()
                log_message = "User is being detected with such NameID, adding to Saml2 table..."
            else:
                user_dict = {
                    "name": _get_random_username_from_email(email)
                    if not config.use_name_from_response()
                    else mapped_data["name"][0],
                    "email": email,
                    "id": str(uuid.uuid4()),
                    "password": str(uuid.uuid4()),
                    "fullname": mapped_data["fullname"][0] if mapped_data.get("fullname") else "",
                }

                log.debug("Trying to create User with name '{}'".format(user_dict["name"]))

                # Before User creation
                for item in p.PluginImplementations(ICKANSAML):
                    item.saml_before_user_create(mapped_data, user_dict)

                new_user = tk.get_action("user_create")({"ignore_auth": True}, user_dict)
                log_message = "User succesfully created. Authorizing..."

            # Make sure that User ID is not already in saml2_user table
            saml_user = model.Session.query(User).filter(User.id == new_user["id"]).first()

            if saml_user:
                log.debug("Found existing row with such User ID, updating NAMEID...")
                saml_user.name_id = nameid
            else:
                saml_user = User(
                    id=new_user["id"],
                    name_id=nameid,
                    attributes=mapped_data,
                )
                model.Session.add(saml_user)
            model.Session.commit()
            log.debug(log_message)
            user = model.User.get(new_user["name"])
        except Exception as e:
            log.exception("Cannot create SAML2 user")
            return h.redirect_to(h.url_for("user.login"))
    else:
        user = model.User.get(saml_user.id)

    user_dict = user.as_dict()
    saml_user.attributes = mapped_data

    # Compare User data if update is needed.
    check_fields = config.user_fields_trigger_update()
    update_dict = {}

    for field in check_fields:
        if mapped_data.get(field):
            updated = True if mapped_data[field][0] != user_dict[field] else False
            if updated:
                update_dict[field] = mapped_data[field][0]

    if user_dict["state"] == "deleted":
        if config.reactivate_deleted_account():
            update_dict["state"] = "active"
            log.debug("Restore deleted user %s", user_dict["name"])

        else:
            log.warning("Blocked login attempt for deleted user %s", user_dict["name"])

            h.flash_error(tk._("Your account was deleted. Please, contact the administrator if you want to restore it"))
            return tk.abort(403)

    if update_dict:
        for item in update_dict:
            user_dict[item] = update_dict[item]

        # username can be changed only if user is in pending state
        user.state = "pending"
        try:
            tk.get_action("user_update")({"ignore_auth": True}, user_dict)
        except tk.ValidationError:
            log.exception("SSO user cannot be updated")
            h.flash_error("This account is not available. Contact portal administration for support.")
            return h.redirect_to(h.url_for("saml.saml_login"))

    model.Session.commit()

    # Roles and Organizations
    for item in p.PluginImplementations(ICKANSAML):
        item.roles_and_organizations(mapped_data, auth, user)

    if tk.check_ckan_version("2.10"):
        duration_time = timedelta(milliseconds=int(tk.config.get(config.CONFIG_TTL, config.DEFAULT_TTL)))

        tk.login_user(user, duration=duration_time)
    else:
        session["samlUserdata"] = auth.get_attributes()
        session["samlNameIdFormat"] = auth.get_nameid_format()
        session["samlNameId"] = nameid
        session["samlCKANuser"] = user.name
        session["samlLastLogin"] = datetime.utcnow()

        tk.g.user = user.name

    if "RelayState" in req["post_data"] and req["post_data"]["RelayState"]:
        log.info('Redirecting to "{}"'.format(req["post_data"]["RelayState"]))
        return h.redirect_to(req["post_data"]["RelayState"])

    return tk.redirect_to(_destination())


@saml.route("/saml/metadata")
def metadata():
    try:
        context = dict(model=model, user=tk.g.user, auth_user_obj=tk.g.userobj)
        tk.check_access("sysadmin", context)
    except tk.NotAuthorized:
        tk.abort(403, tk._("Need to be system administrator to administer"))

    req = utils.prepare_from_flask_request()
    auth = utils.make_auth(req)

    settings = auth.get_settings()
    metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(metadata)

    if len(errors) == 0:
        resp = make_response(metadata, 200)
        resp.headers["Content-Type"] = "text/xml"
    else:
        resp = make_response(", ".join(errors), 500)
    return resp


@saml.route("/saml/login")
def saml_login():
    req = utils.prepare_from_flask_request()
    try:
        auth = utils.make_auth(req)

        if tk.asbool(tk.request.args.get("sso")) or config.unconditional_login():
            saml_relaystate = tk.config.get("ckan.saml_relaystate", None)
            redirect = saml_relaystate if saml_relaystate else _destination()
            if tk.request.args.get("redirect"):
                redirect = tk.request.args.get("redirect")

            if tk.g.user:
                return h.redirect_to(redirect)

            log.info("Redirect to SAML IdP.")
            return h.redirect_to(auth.login(return_to=redirect))
        else:
            log.warning(
                "No arguments been provided in this URL. If you want to make"
                " auth request to SAML IdP point, please provide '?sso=true'"
                " at the end of the URL."
            )
    except Exception as e:
        h.flash_error("SAML: An issue appeared while validating settings file.")
        log.error(f"{e}")

    return h.redirect_to(h.url_for("user.login"))


def _destination() -> str:
    dynamic = tk.request.args.get("came_from", "")
    static = tk.config.get("ckan.auth.route_after_login", "dashboard.index")
    return dynamic or static
