from datetime import datetime, date, time , timedelta
import random

from conference_scheduler.resources import Slot, Event
from conference_scheduler import scheduler
from conference_scheduler.lp_problem import objective_functions


def get_slots_for_ward(year , week  , ward , capacity):
    partial_date = "{0}-W{1}".format(year , week)

    slots = []

    start_date  = datetime.strptime(partial_date + '-1', "%Y-W%W-%w")
    s_shift = start_date
    for day in range(0, 6):

        d_day = start_date + timedelta(days=day)


        for shift in range(0, 24 ,8):

            s_shift =  d_day +  timedelta(hours=shift)

            slot = Slot(venue=ward, starts_at=s_shift, duration=60 * 8 , session= ward +"_" + str(day)+ "_" + str(shift), capacity=capacity)
            slots.append(slot)
    return slots

def get_nurse_events(employee_name , unavilable_slots ):
    employee_events = []

    for day in range(0 , 7):

        event = Event(name=employee_name +'_'  + str(day) , duration=60 * 8 , tags=[employee_name] ,
                        demand=3 )
        employee_events.append(event)

    return employee_events

def get_nurse_events_2(employee_name , unavilable_slots ):
    employee_events = []
    for day in range(0 , 7):
        selected = random.sample([1,2,3] ,1 )
        event1 = Event(name=employee_name + '_e1_' + '_' + str(day) , duration=60 * 8 , tags=[employee_name] ,
                        demand=0)
        event2 = Event(name=employee_name + '_e2_' + '_' + str(day) , duration=60 * 8 , tags=[employee_name] ,
                         demand=0)

        event3 = Event(name=employee_name + '_e4_' + '_' + str(day) , duration=60 * 8 , tags=[employee_name] ,
                        demand=0)



        employee_events.append(event1)
        employee_events.append(event2)
        employee_events.append(event3)

        if selected ==1:
            event1.add_unavailability(event2)
            event1.add_unavailability(event3)
        elif selected == 2 :
            event2.add_unavailability(event1)
            event2.add_unavailability(event3)
        elif selected == 3:
            event3.add_unavailability(event1)
            event3.add_unavailability(event2)

    return employee_events




def main():
    wards = ["ER" , "OPD" , "SURG"]
    all_slots = []
    all_events = []
    for ward in wards:
        slots = get_slots_for_ward(2017,1, ward , 3)
        all_slots = all_slots  + slots


    nurses = ["latifa bibi" , "salma" , "nadia" , "nazia" , "munir" , "shamim" , "Nasreen" ]
    un_available_slots = []

    for nurse in nurses:
        nurse_events = get_nurse_events(nurse ,un_available_slots)
        all_events =  all_events  + nurse_events

    for e in all_events:
        print(e)

    #func = objective_functions.efficiency_capacity_demand_difference
    func = objective_functions.equity_capacity_demand_difference

    schedule = scheduler.schedule(all_events  , all_slots , objective_function=func)
    schedule.sort(key=lambda item: item.slot.starts_at)
    for item in schedule:
        print(f"{item.event.tags[0]} at {item.slot.starts_at} in {item.slot.venue}")





if __name__ == '__main__':
    main()








