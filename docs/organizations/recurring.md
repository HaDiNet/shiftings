# Recurring Shifts

## Creating Recurring Shift
To use recurring Shifts you have to first build a time frame.

This has multiple Parameters:

* **Time Frame Type** - The basic repetition of the Shift will be explained in further Detail below.
* **Ordinal** - What number should the "*Nth*" in the time Frame Type be replaced with.
* **Day of the Week** - What day should the "*weekday*" in the time Frame Type be replaced with.
* **Month** - What day should the "*month*" in the time Frame Type be replaced with.
* **First Occurrence** - When should the Shift be created the first time.

### Time Frame Types
The following Time Frame Types are available:

* '`Nth` `weekday` of each month' - The Recurring Shift will be every `Nth` `weekday` of each month. 
If N is 1 it will be every week. 
* '`Nth` day of each month' - The Recurring Shift will be every `Nth` day of each month. 
If N is 5 it will always be on the 5th.
* 'every `Nth` `weekday`' - The Recurring Shift will be every `Nth` `weekday`. 
If N is 2, the weekday is Sunday and a month has 5 Sundays the next month will have the shift on the 1st Sunday.
* '`Nth` workday of each month' - The Recurring Shift will on the `Nth` working day of each Month.
if N is 1 and the first day of the month is a Sunday the shift will be on the following Monday.
* '`Nth` day of `month`' - The Recurring Shift will on the `Nth` day of the selected `month` every year.
if N is 1 and the month is January is will create Shifts on every 1st of January every year.
* '`Nth` workday of `month`' - The Recurring Shift will on the `Nth` working day of the selected `month`.
if N is 1 and the first day of the selected month is a Sunday the shift will be on the following Monday.

## Creating Shifts from Recurring Shifts
Recurring Shifts have to be created using the "*create_recurring_shifts*" command.

Optimally this is executed daily as a cron job oder systemd timer:
```
0 0 * * * /path/to/manage.py create_recurring_shifts > /dev/null 2>&1
```

## Templates
Recurring Shifts are always created from [Organization Templates](shift_templates.md) 
