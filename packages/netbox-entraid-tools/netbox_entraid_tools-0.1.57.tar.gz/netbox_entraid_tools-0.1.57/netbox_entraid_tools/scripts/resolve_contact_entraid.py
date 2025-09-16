from extras.scripts import Script, ObjectVar, MultiObjectVar, BooleanVar
from tenancy.models import Contact
from netbox_entraid_tools.entra.graph import GraphClient
from netbox_entraid_tools.common import contact_payload_from_user
from django.conf import settings
from difflib import get_close_matches


class ResolveContactEntraID(Script):
    class Meta:
        name = "Resolve Contact(s) against EntraID"
        description = "Match and update NetBox contacts with EntraID users via email or fuzzy name."
        field_order = ["contacts", "dry_run"]

    contacts = MultiObjectVar(
        model=Contact,
        required=True,
        description="Select one or more contacts to resolve against EntraID.",
    )
    dry_run = BooleanVar(
        default=True, description="If checked, no changes will be made."
    )

    def run(self, data, commit):
        client = GraphClient()
        results = []

        # Check if we're being called from a job (has custom logger)
        self.has_job_logger = hasattr(self, "logger")

        # Helper method to handle logging with proper method calls
        def log_message(level, message):
            if self.has_job_logger:
                # Use the job logger's methods
                if level == "info":
                    self.logger.info(message)
                elif level == "warning":
                    self.logger.warning(message)
                elif level == "success":
                    self.logger.success(message)
                elif level == "failure":
                    self.logger.failure(message)
                elif level == "debug":
                    self.logger.debug(message)
            else:
                # Use the script's built-in methods
                if level == "info":
                    self.log_info(message)
                elif level == "warning":
                    self.log_warning(message)
                elif level == "success":
                    self.log_success(message)
                elif level == "failure":
                    self.log_failure(message)
                elif level == "debug":
                    # Standard Script class doesn't have debug logging
                    # Fall back to info level with a debug prefix for visibility
                    self.log_info(f"DEBUG: {message}")

        for contact in data["contacts"]:
            # If contact is an int, resolve to Contact object
            if isinstance(contact, int):
                contact_obj = Contact.objects.filter(pk=contact).first()
                if not contact_obj:
                    log_message("warning", f"Contact with pk {contact} not found.")
                    continue
                contact = contact_obj
            email = contact.email
            name = contact.name
            entra_user = None
            # 1. Try email match
            if email:
                entra_user = client.get_user_by_email(email)
            # 2. Fuzzy name match if no email match
            if not entra_user:
                if email:
                    log_message(
                        "info",
                        f"No EntraID user found with email '{email}', trying fuzzy name match",
                    )

                # Extract first letter of name for targeted filtering
                first_letter = name[0].upper() if name else None
                name_filter = None

                # Build name variations before retrieving users
                name_variations = [
                    name,  # Original name: "John Quincy Public"
                    " ".join(reversed(name.split())),  # Reversed: "Public Quincy John"
                    ", ".join(
                        reversed(name.rsplit(" ", 1))
                    ),  # Last, First Middle: "Public, John Quincy"
                ]

                # For names with more than 2 parts, try first + last
                name_parts = name.split()
                if len(name_parts) > 2:
                    name_variations.append(
                        f"{name_parts[0]} {name_parts[-1]}"
                    )  # "John Public"

                # Log the variations we're trying
                log_message("debug", f"Trying name variations: {name_variations}")

                # Use targeted filter if we have a first letter
                if first_letter:
                    # Filter for names starting with the same letter to reduce result set
                    name_filter = f"startswith(displayName,'{first_letter}')"
                    log_message("info", f"Using name filter: {name_filter}")

                # Get users with appropriate filtering
                all_users = client.list_users(name_filter=name_filter)
                log_message(
                    "info",
                    f"Retrieved {len(all_users)} users from EntraID for fuzzy matching",
                )

                # If very few results and we used a first-letter filter, try without filter
                if len(all_users) < 10 and name_filter:
                    log_message(
                        "info",
                        f"Few results with filter, retrieving more users for better matching",
                    )
                    # Try another batch without filtering
                    more_users = client.list_users(full_retrieval=True)
                    log_message(
                        "info",
                        f"Retrieved additional {len(more_users)} users without filtering",
                    )
                    all_users = more_users

                # Extract display names once
                display_names = [u["displayName"] for u in all_users]

                # Try each variation
                for variation in name_variations:
                    matches = get_close_matches(
                        variation, display_names, n=5, cutoff=0.6
                    )

                    if matches:
                        # We found matches for this variation
                        log_message(
                            "info",
                            f"Fuzzy matches for '{variation}': {matches}",
                        )
                        # Use the first (closest) match
                        match_name = matches[0]
                        entra_user = next(
                            u for u in all_users if u["displayName"] == match_name
                        )
                        # Check if the matched user is disabled
                        if entra_user.get("accountEnabled") is False:
                            log_message(
                                "info",
                                f"Note: Matched user '{match_name}' is disabled in EntraID but will be used anyway",
                            )
                        break
                else:
                    log_message(
                        "warning", f"No EntraID match found for contact '{name}'."
                    )
                    continue
            if entra_user:
                # Log account status for better troubleshooting
                account_status = (
                    "enabled" if entra_user.get("accountEnabled") else "disabled"
                )

                log_message(
                    "success",
                    f"Matched contact '{name}' to EntraID user '{entra_user['displayName']}' ({entra_user['id']}) [{account_status}]",
                )

                payload = contact_payload_from_user(entra_user)
                if commit and not data["dry_run"]:
                    # Update contact fields from payload (NetBox ORM)
                    for field, value in payload.items():
                        if field == "entra_oid":
                            contact.custom_field_data["entra_oid"] = value
                        else:
                            setattr(contact, field, value)
                    contact.save()
            else:
                log_message("failure", f"No match for contact '{name}'.")
        return f"Processed {len(data['contacts'])} contact(s)."
