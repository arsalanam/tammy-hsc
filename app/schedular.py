from datetime import datetime , date , time , timedelta
import random

from conference_scheduler.resources import Slot , Event
from conference_scheduler import scheduler
from conference_scheduler.lp_problem import objective_functions

from .models import  Ward , Nurse
from . import  db

def get_slots_for_ward(year , week , ward , capacity):
    partial_date = "{0}-W{1}".format(year , week)

    slots = []

    start_date = datetime.strptime(partial_date + '-1' , "%Y-W%W-%w")
    s_shift = start_date
    for day in range(0 , 7):

        d_day = start_date + timedelta(days=day)

        for shift in range(0 , 24 , 8):
            s_shift = d_day + timedelta(hours=shift)

            slot = Slot(venue=ward , starts_at=s_shift , duration=60 * 8 ,
                        session=ward + "_" + str(day) + "_" + str(shift) , capacity=capacity)
            slots.append(slot)
    return slots


def get_nurse_events(employee_name , unavilable_slots):
    employee_events = []

    for day in range(0 , 7):
        event = Event(name=employee_name + '_' + str(day) , duration=60 * 8 , tags=[employee_name] ,
                      demand=3)
        employee_events.append(event)

    return employee_events


def get_nurse_events_2(employee_name , unavilable_slots):
    employee_events = []
    unavailable_events = []
    for day in range(0 , 7):
        selected = random.sample([1 , 2 , 3] , 1)
        event1 = Event(name=employee_name + '_e1_' + '_' + str(day) , duration=60 * 8 , tags=[employee_name] ,
                       demand=3 , unavailability=unavilable_slots)
        event2 = Event(name=employee_name + '_e2_' + '_' + str(day) , duration=60 * 8 , tags=[employee_name] ,
                       demand=3 , unavailability=unavilable_slots)

        event3 = Event(name=employee_name + '_e3_' + '_' + str(day) , duration=60 * 8 , tags=[employee_name] ,
                       demand=3 , unavailability=unavilable_slots)

        if selected == 1:
            employee_events.append(event1)
            unavailable_events = [event2 , event3]
        elif selected == 2:
            employee_events.append(event2)
            unavailable_events = [event1 , event3]
        else:
            employee_events.append(event3)
            unavailable_events = [event1 , event2]

    return employee_events , unavailable_events


def main_schedule(year,week,capacity):
    wards = []
    wards_list = db.session.query(Ward).all()
    for item in wards_list:
        wards.append(item.name)

    all_slots = []
    all_events = []

    ward_slot = {}
    for ward in wards:

        slots = get_slots_for_ward( year, week , ward , capacity)
        ward_slot[ward] = slots
        all_slots = all_slots + slots


    nurses = db.session.query(Nurse).all()


    for entry in nurses:
        nurse = entry.first_name + entry.last_name
        unavilable_slots = []
        secure_random = random.SystemRandom()
        selected_ward = secure_random.choice(wards)

        remaining = [item for item in wards if item != selected_ward]

        for item in remaining:
            unavilable_slots = unavilable_slots + ward_slot[item]

        nurse_event , un_valiable = get_nurse_events_2(nurse , unavilable_slots)

        for entry in un_valiable:
            nurse_event[0].add_unavailability(entry)

        all_events = all_events + nurse_event



    func = objective_functions.efficiency_capacity_demand_difference
    # func = objective_functions.equity_capacity_demand_difference

    schedule = scheduler.schedule(all_events , all_slots)
    schedule.sort(key=lambda item: item.slot.starts_at)

    out_put = []

    for item in schedule:

        line = 'Nurse {0}  at {1} in {2} '.format(item.event.tags[0] , item.slot.starts_at, item.slot.venue)
        out_put.append(line)

    return out_put



