"""
Actions module - Action definitions and effects.

Available actions (v0):
- WORK_SHIFT
- REST
- EAT
- COMMUTE
- SOCIALIZE
- JOB_SEARCH
- HOUSING_CHANGE

Enhanced actions (v1):
- GO_ON_DATE
- PROPOSE
- GET_MARRIED
- VISIT_FRIEND
- ATTEND_EVENT
- GO_SHOPPING

Actions are proposals. The world enforces legality, cost, and consequences.
"""

from urbanium.actions.base import Action, ActionType
from urbanium.actions.work import WorkShiftAction
from urbanium.actions.rest import RestAction
from urbanium.actions.eat import EatAction
from urbanium.actions.commute import CommuteAction
from urbanium.actions.socialize import SocializeAction
from urbanium.actions.job_search import JobSearchAction
from urbanium.actions.housing import HousingChangeAction
from urbanium.actions.social_actions import (
    GoOnDateAction,
    ProposeAction,
    GetMarriedAction,
    VisitFriendAction,
    AttendEventAction,
    GoShoppingAction,
    get_social_actions,
)

__all__ = [
    "Action",
    "ActionType",
    # v0 actions
    "WorkShiftAction",
    "RestAction",
    "EatAction",
    "CommuteAction",
    "SocializeAction",
    "JobSearchAction",
    "HousingChangeAction",
    # v1 social actions
    "GoOnDateAction",
    "ProposeAction",
    "GetMarriedAction",
    "VisitFriendAction",
    "AttendEventAction",
    "GoShoppingAction",
    # Helper functions
    "get_available_actions",
    "get_all_actions",
    "get_social_actions",
]


def get_all_actions() -> list:
    """
    Get all action instances.
    
    Returns:
        List of all action objects
    """
    base_actions = [
        WorkShiftAction(),
        RestAction(),
        EatAction(),
        CommuteAction(),
        SocializeAction(),
        JobSearchAction(),
        HousingChangeAction(),
    ]
    
    # Add social actions
    base_actions.extend(get_social_actions())
    
    return base_actions


def get_available_actions(citizen, local_state: dict) -> list:
    """
    Get all available actions for a citizen given the current state.
    
    Actions must satisfy prerequisites to be available.
    """
    all_actions = get_all_actions()
    
    available = []
    for action in all_actions:
        if action.check_prerequisites(citizen, local_state):
            available.append(action)
    
    return available
