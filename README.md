# Calendar Generator

## 1) Introduction

The goal of this project is to read a timeline written in human language and translate it to ICalendar file format

__Expected file format:__

```
Semaine du <jour>/<mois>

<jour de la semaine> <heure de début>H<minute de début>-<heure de fin>H<minute de fin>: <titre> (<intervenant>)
<jour de la semaine> <heure de début>H<minute de début>-<heure de fin>H<minute de fin>: <titre> (<intervenant>)
<jour de la semaine> <heure de début>H<minute de début>-<heure de fin>H<minute de fin>: <titre> (<intervenant>)

Semaine du <jour>/<mois>

<jour de la semaine> <heure de début>H<minute de début>-<heure de fin>H<minute de fin>: <titre> (<intervenant>)
<jour de la semaine> <heure de début>H<minute de début>-<heure de fin>H<minute de fin>: <titre> (<intervenant>)
<jour de la semaine> <heure de début>H<minute de début>-<heure de fin>H<minute de fin>: <titre> (<intervenant>)

...
```

Please note that you can add several events in the same line by separating each event with a slash

