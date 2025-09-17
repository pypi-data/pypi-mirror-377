from __future__ import annotations

import csv
import os
from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django_pandas.io import read_frame

from edc_pdutils.constants import SYSTEM_COLUMNS
from edc_sites.site import sites
from edc_utils import get_utcnow

from .site_randomizers import site_randomizers


class RandomizationListExporterError(Exception):
    pass


class SubjectNotRandomization(Exception):
    pass


def get_assignment_for_subject(
    subject_identifier: str,
    randomizer_name: str = None,
    identifier_fld: str | None = None,
) -> str:
    """Returns the assignment for a randomized subject.

    Calling this method before a subject is randomized will
    raise a SubjectNotRandomization error.
    """
    obj = get_object_for_subject(
        subject_identifier, randomizer_name, identifier_fld=identifier_fld
    )
    return obj.assignment


def get_assignment_description_for_subject(
    subject_identifier: str,
    randomizer_name: str = None,
    identifier_fld: str | None = None,
) -> str:
    """Returns the assignment description for a randomized subject.

    Calling this method before a subject is randomized will
    raise a SubjectNotRandomization error.
    """
    randomizer_cls = site_randomizers.get(randomizer_name)
    return randomizer_cls.assignment_description_map.get(
        get_assignment_for_subject(
            subject_identifier, randomizer_name, identifier_fld=identifier_fld
        )
    )


def get_object_for_subject(
    subject_identifier: str,
    randomizer_name: str = None,
    identifier_fld: str | None = None,
    label: str | None = None,
) -> Any:
    """Returns a randomization list model instance or raises
    for the given subject.

    Calling this method before a subject is randomized will
    raise a SubjectNotRandomization error.
    """
    identifier_fld = identifier_fld or "subject_identifier"
    label = label or "subject"
    randomizer_cls = site_randomizers.get(randomizer_name)
    opts = {
        identifier_fld: subject_identifier,
        "randomizer_name": randomizer_name,
        "allocated": True,
        "allocated_datetime__isnull": False,
    }
    try:
        obj = randomizer_cls.model_cls().objects.get(**opts)
    except ObjectDoesNotExist:
        raise SubjectNotRandomization(
            f"{label.title()} not randomized. See Randomizer `{randomizer_name}`. "
            f"Got {identifier_fld}=`{subject_identifier}`."
        )
    return obj


def generate_fake_randomization_list(
    all_sites=None,
    country=None,
    site_name=None,
    assignment: list | None = None,
    slots: int | None = None,
    write_header: bool | None = None,
    filename=None,
    assignment_map=None,
):
    """
    Generate a dummy randomization list.

    This trial is randomized by site so all assignments are
    the same within a site. Use this util to generate a dummy
    randomization_list.csv for import into the RandomizationList
    model. Patient registration always refers to and updates the
    RandomizationList model.

    Add slots to a dummy `randomization` list file where all
    assignments are the same for each slot.
    """
    slots = slots or 10
    assignment_map = assignment_map or ["intervention", "control"]
    if assignment not in assignment_map:
        raise ValueError(f"Invalid assignment. Got {assignment}")

    # get site ID and write the file
    site_id = sites.get_by_attr("name", site_name)
    with open(filename, "a+", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["sid", "assignment", "site_name", "country"])
        if write_header:
            writer.writeheader()
        for j in range(1, int(slots)):
            sid = str(j).zfill(len(str(slots)))
            writer.writerow(
                dict(
                    sid=f"{site_id}{sid}",
                    assignment=assignment,
                    site_name=site_name,
                    country=country,
                )
            )

    print(f"(*) Added {slots} slots for {site_name}.")


def export_randomization_list(
    randomizer_name: str, path: str | None = None, username: str | None = None
):
    randomizer_cls = site_randomizers.get(randomizer_name)

    try:
        user = get_user_model().objects.get(username=username)
    except ObjectDoesNotExist:
        raise RandomizationListExporterError(f"User `{username}` does not exist")
    if not user.has_perm(randomizer_cls.model_cls()._meta.label_lower.replace(".", ".view_")):
        raise RandomizationListExporterError(
            f"User `{username}` does not have "
            f"permission to view '{randomizer_cls.model_cls()._meta.label_lower}'"
        )
    path = path or settings.EXPORT_FOLDER
    timestamp = get_utcnow().strftime("%Y%m%d%H%M")
    filename = os.path.expanduser(
        f"~/{settings.APP_NAME}_{randomizer_cls.name}_"
        f"randomizationlist_exported_{timestamp}.csv"
    )
    filename = os.path.join(path, filename)

    df = (
        read_frame(randomizer_cls.model_cls().objects.all(), verbose=False)
        .drop(columns=SYSTEM_COLUMNS)
        .sort_values(["sid"])
        .reset_index(drop=True)
    )

    opts = dict(
        path_or_buf=filename,
        encoding="utf-8",
        index=0,
        sep="|",
    )
    df.to_csv(**opts)
    print(filename)
    return filename
