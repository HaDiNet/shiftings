# Shift Templates

## Groups
Shift Templates are Groups of multiple Shifts that can be created together.
This way you only need one Template per Event.

## Creating a Shift Template
First you only need the basic Information:

* **Name** - Name of the Template Group this is only for adding it to other objects.
* **Place** - Where this Template Group should take Place. This will be added to Shifts
* **Start Time** - Time from which on the Templates will be converted to Shifts

After Creating a Group you can add Shifts to the templates.
Every Template needs:

* **Name** - Name of the Shift as Presented to the Users
* **Shift Type** - For grouping in the Shift Summary
* **Users** - Required and maximum amount of users in the Shift. If Maximum is 0 any Number of People is allowed.
* **Time** - A Start Delay will be Added to the Start Time configured in the Group. The Duration is Applied on top of that.
A Shift Template with a start time of 1pm, a delay of 1h and a duration of 1h will therefore last from 2pm to 3pm.
You can add multiple Shift templates at once. If you want to delete a Template ist will be marked as to delete and removed once you save.
* **Additional Infos** - Additional Infos will be displayed in every Shift.