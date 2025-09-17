# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json
from restclients_core import models


class Library(models.Model):
    name = models.CharField(max_length=250, null=True)
    description = models.CharField(max_length=1000, null=True)
    url = models.CharField(max_length=250, null=True)


class Librarian(models.Model):
    name = models.CharField(max_length=250, null=True)
    email = models.CharField(max_length=100, null=True)
    phone = models.CharField(max_length=20, null=True)
    url = models.CharField(max_length=250, null=True)


class CourseGuide(models.Model):
    guide_url = models.CharField(max_length=250, null=True)
    guide_text = models.CharField(max_length=1000, null=True)


class SubjectGuide(models.Model):
    contact_url = models.CharField(max_length=250, null=True)
    contact_text = models.CharField(max_length=1000, null=True)
    discipline = models.CharField(max_length=250, null=True)
    find_librarian_url = models.CharField(max_length=250, null=True)
    find_librarian_text = models.CharField(max_length=1000, null=True)
    guide_url = models.CharField(max_length=250, null=True)
    guide_text = models.CharField(max_length=1000, null=True)
    faq_url = models.CharField(max_length=250, null=True)
    faq_text = models.CharField(max_length=1000, null=True)
    writing_guide_url = models.CharField(max_length=250, null=True)
    writing_guide_text = models.CharField(max_length=1000, null=True)
    is_default_guide = models.NullBooleanField()
    default_guide_campus = models.CharField(max_length=50, null=True)
    course_guide = models.ForeignKey(CourseGuide, null=True)


class MyLibAccount(models.Model):
    holds_ready = models.IntegerField()
    fines = models.DecimalField(max_digits=8, decimal_places=2)
    items_loaned = models.IntegerField()
    next_due = models.DateTimeField(null=True)

    def get_next_due_date_str(self):
        """
        return next due date in the ISO format (yyyy-mm-dd).
        If the next_due is None, return None.
        """
        if self.next_due is not None:
            return self.next_due.isoformat()  # 2020-07-15T02:00:00+00:00
        return None

    def json_data(self):
        return {'holds_ready': self.holds_ready,
                'fines': self.fines,
                'items_loaned': self.items_loaned,
                'next_due': self.get_next_due_date_str()
                }

    def __str__(self):
        return json.dumps(self.json_data())
