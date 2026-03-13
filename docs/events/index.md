# Events

**ATTENTION: Events are still under development and not yet available for use in the current version.**

## Overview

Events are high-level organizational containers that group related shifts together around a specific occasion, festival, conference, or multi-day program. An Event provides central coordination for multiple shifts, allowing organizations to manage comprehensive staffing operations for complex undertakings that span multiple days and require various shift types.

Think of an Event as a parent container: while individual [Shifts](../shifts.md) represent specific time slots with particular work assignments, Events bundle these shifts together with unified contact information, branding, and staffing visibility.

## Purpose of Events

Events serve several key functions in the Shiftings system:

### 1. Shift Organization

Events group logically related shifts, making it easier for both coordinators to manage schedules and volunteers to understand the scope of an opportunity. Rather than viewing dozens of isolated shifts, volunteers see them as part of a cohesive event.

### 2. Event-Level Contact & Branding

Each Event can have its own:

- **Official name** and description
- **Logo and branding**
- **Contact information**: email address, phone number, website
- **Date range**: defining when shifts are available

This allows large, complex events to maintain consistent contact information across all their shifts, and enables volunteers to find event-specific resources and communication channels.

### 3. Staffing Overview

Events provide aggregate metrics for coordinators to monitor overall staffing:

- **Shifts needing more participants** (by required user count)
- **Open shifts available** for signup
- **Filled slots vs. needed slots** across all event shifts
- Visibility into overall staffing health at a glance

### 4. Unified Participation Management

Organizations can set participation permissions at the Event level, which all contained shifts inherit. This simplifies permission management when you want the same participation rules across an entire event.

## Key Event Attributes

| Attribute | Type | Purpose |
| ----------- | ------ | --------- |
| **Name** | Text | Display name of the event (required) |
| **Organization** | Foreign Key | The organization that owns the event (required) |
| **Start Date** | Date | Earliest date where shifts are available (helps with filtering) |
| **End Date** | Date | Latest date where shifts are available |
| **Description** | Text | Detailed information about the event (optional) |
| **Logo** | Image | Event branding (optional; auto-resized to maximum size) |
| **Email** | Email | Primary contact email for event questions |
| **Telephone Number** | Phone | Contact phone number |
| **Website** | URL | Link to event website or more information |

### Date Constraints

- Start Date must be less than or equal to End Date
- These dates help volunteers and coordinators quickly identify which events are currently active or when an event is scheduled

## Shifts and Events

Every shift can optionally be associated with an Event. When a shift references an event:

- The **shift's email address** defaults to the event's email (if set), otherwise uses the organization's email
- The shift **inherits participation permissions** from the event (in addition to organization-level permissions)
- The shift appears in the event's shift list and contributes to event staffing metrics

A shift being associated with an Event is **optional**—organizations can also create standalone shifts that aren't part of any formal event.

### Validation

Shiftings enforces consistency: if a shift is linked to an event, both **must belong to the same organization**. This prevents accidental misalignment between event and shift ownership.

## Participation and Permissions

Events support participation permission settings that cascade to contained shifts. Organizations can granularly control:

- **Who can see the event exists**
- **Who can see shift details** (dates, descriptions, participant names)
- **Who can view participant lists**
- **Who can participate in shifts**

These permissions work alongside organization-level and shift-specific permissions, allowing flexible access control from the broadest (organization) to most specific (individual shift) level.

## Example Use Case

Imagine organizing a **two-day music festival**:

**Event:** "Heimfest 2026" (May 29-31)

- Logo: Festival branding image  
- Email: <helfen-heimfest@hadiko.de>
- Website: <https://www.hadiko.de>
- Description: "Help us create an amazing experience!"

**Associated Shifts:**

- "Security Team - Friday 10am-6pm" (May 29)
- "Ticket Booth - Saturday 9am-5pm" (May 30)
- "Beer Sales - Saturday 9am-12pm" (May 30)
- "Cleanup Crew - Sunday 11am-4pm" (May 31)
- "Catering Support - Friday 4pm-11pm" (May 29)

With this structure:

- Volunteers see the festival as one opportunity, not five isolated shifts
- All shifts share the festival's contact info and logo
- Coordinators can instantly see that 12 people are needed for Friday shifts, but only 8 have signed up
- Participation rules (e.g., volunteers must be 18+) can be set once at the event level
- The festival runs from May 29-31, and any shifts outside this range would be considered anomalies

## Display and Access

Events appear in organization interfaces and can be filtered by date range. The event's display format shows:

```text
{Event Name} (by {Organization Name})
```

This grouping makes it immediately clear which organization is running each event, useful in multi-organization environments.
