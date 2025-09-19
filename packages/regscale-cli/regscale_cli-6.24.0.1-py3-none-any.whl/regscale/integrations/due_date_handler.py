#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Due Date Handler for Scanner Integrations"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from regscale.core.app.application import Application
from regscale.core.utils.date import date_str, get_day_increment
from regscale.integrations.public.cisa import pull_cisa_kev
from regscale.models import regscale_models
from regscale.utils.threading import ThreadSafeDict

logger = logging.getLogger("regscale")


class DueDateHandler:
    """
    Handles due date calculations for scanner integrations based on:
    1. Init.yaml timeline configurations per integration
    2. KEV (Known Exploited Vulnerabilities) dates from CISA
    3. Default severity-based timelines
    """

    def __init__(self, integration_name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the DueDateHandler for a specific integration

        :param str integration_name: Name of the integration (e.g., 'wiz', 'qualys', 'tenable')
        :param Optional[Dict[str, Any]] config: Optional config override, uses Application config if None
        """
        self.integration_name = integration_name.lower()
        self.config = config or Application().config
        self._kev_data: Optional[ThreadSafeDict] = None

        # Default due date timelines (days)
        self.default_timelines = {
            regscale_models.IssueSeverity.Critical: 30,
            regscale_models.IssueSeverity.High: 60,
            regscale_models.IssueSeverity.Moderate: 120,
            regscale_models.IssueSeverity.Low: 364,
        }

        # Load integration-specific timelines from config
        self.integration_timelines = self._load_integration_timelines()

    def _load_integration_timelines(self) -> Dict[regscale_models.IssueSeverity, int]:
        """
        Load timeline configurations for this integration from init.yaml

        :return: Dictionary mapping severity to days
        :rtype: Dict[regscale_models.IssueSeverity, int]
        """
        timelines = self.default_timelines.copy()

        issues_config = self.config.get("issues", {})
        integration_config = issues_config.get(self.integration_name, {})

        if integration_config:
            logger.debug(f"Found timeline config for {self.integration_name}: {integration_config}")

            # Map config keys to severity levels
            severity_mapping = {
                "critical": regscale_models.IssueSeverity.Critical,
                "high": regscale_models.IssueSeverity.High,
                "moderate": regscale_models.IssueSeverity.Moderate,
                "medium": regscale_models.IssueSeverity.Moderate,  # Some integrations use 'medium'
                "low": regscale_models.IssueSeverity.Low,
            }

            for config_key, severity in severity_mapping.items():
                if config_key in integration_config:
                    timelines[severity] = integration_config[config_key]

        return timelines

    def _get_kev_data(self) -> ThreadSafeDict:
        """
        Get KEV data from CISA, using cache if available

        :return: Thread-safe dictionary containing KEV data
        :rtype: ThreadSafeDict
        """
        if self._kev_data is None:
            try:
                kev_data = pull_cisa_kev()
                self._kev_data = ThreadSafeDict()
                self._kev_data.update(kev_data)
                logger.debug("Loaded KEV data from CISA")
            except Exception as e:
                logger.warning(f"Failed to load KEV data: {e}")
                self._kev_data = ThreadSafeDict()

        return self._kev_data

    def _should_use_kev(self) -> bool:
        """
        Check if this integration should use KEV dates

        :return: True if KEV should be used for this integration
        :rtype: bool
        """
        issues_config = self.config.get("issues", {})
        integration_config = issues_config.get(self.integration_name, {})
        return integration_config.get("useKev", True)  # Default to True if not specified

    def _get_kev_due_date(self, cve: str) -> Optional[str]:
        """
        Get the KEV due date for a specific CVE

        :param str cve: The CVE identifier
        :return: KEV due date string if found, None otherwise
        :rtype: Optional[str]
        """
        if not self._should_use_kev() or not cve:
            return None

        kev_data = self._get_kev_data()

        # Find the KEV entry for this CVE
        kev_entry = next(
            (entry for entry in kev_data.get("vulnerabilities", []) if entry.get("cveID", "").upper() == cve.upper()),
            None,
        )

        if kev_entry:
            kev_due_date = kev_entry.get("dueDate")
            if kev_due_date:
                logger.debug(f"Found KEV due date for {cve}: {kev_due_date}")
                return kev_due_date

        return None

    def calculate_due_date(
        self,
        severity: regscale_models.IssueSeverity,
        created_date: str,
        cve: Optional[str] = None,
        title: Optional[str] = None,
    ) -> str:
        """
        Calculate the due date for an issue based on severity, KEV status, and integration config

        :param regscale_models.IssueSeverity severity: The severity of the issue
        :param str created_date: The creation date of the issue
        :param Optional[str] cve: The CVE identifier (if applicable)
        :param Optional[str] title: The title of the issue (for additional context)
        :return: The calculated due date string
        :rtype: str
        """
        # First, check if this CVE has a KEV due date
        if cve:
            kev_due_date = self._get_kev_due_date(cve)
            if kev_due_date:
                # Parse the KEV due date and created date
                try:
                    from dateutil.parser import parse as date_parse

                    kev_date = date_parse(kev_due_date).date()
                    created_dt = date_parse(created_date).date()

                    # If KEV due date is after creation date, use KEV date
                    # If KEV due date is before creation date, add the difference to creation date
                    if kev_date >= created_dt:
                        logger.debug(f"Using KEV due date {kev_due_date} for CVE {cve}")
                        return kev_due_date
                    else:
                        # KEV date has passed, calculate new due date from creation
                        days_diff = (created_dt - kev_date).days
                        # Give at least 30 days from creation for critical KEV items
                        adjusted_days = max(30, days_diff)
                        due_date = date_str(get_day_increment(start=created_date, days=adjusted_days))
                        logger.debug(f"KEV date passed, using adjusted due date {due_date} for CVE {cve}")
                        return due_date

                except Exception as e:
                    logger.warning(f"Failed to parse KEV due date {kev_due_date}: {e}")

        # Fall back to severity-based timeline from integration config
        days = self.integration_timelines.get(severity, self.default_timelines[severity])
        due_date = date_str(get_day_increment(start=created_date, days=days))

        logger.debug(f"Using {self.integration_name} timeline: {severity.name} = {days} days, due date = {due_date}")

        return due_date

    def get_integration_config(self) -> Dict[str, Any]:
        """
        Get the full integration configuration from init.yaml

        :return: Integration configuration dictionary
        :rtype: Dict[str, Any]
        """
        issues_config = self.config.get("issues", {})
        return issues_config.get(self.integration_name, {})

    def get_timeline_info(self) -> Dict[str, Any]:
        """
        Get information about current timeline configuration

        :return: Dictionary with timeline information
        :rtype: Dict[str, Any]
        """
        return {
            "integration_name": self.integration_name,
            "use_kev": self._should_use_kev(),
            "timelines": {severity.name: days for severity, days in self.integration_timelines.items()},
            "config_source": "init.yaml",
        }
