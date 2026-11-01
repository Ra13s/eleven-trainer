# Create a session

Start with a local export in `.local/source.json`; see the [tutorial](../tutorials/first-training.md) if you have not exported one. Commands here assume the chosen Python interpreter is available as `python`, and run from the repository root.

## Practice one serve or stroke

List the source file and identify the desired shot ID:

```console
python -m eleven_trainer list .local/source.json
```

Replace `SHOT_ID` below with that ID. One generated active row lets the game's launcher repeat the same shot, subject to its normal loop behavior:

```console
python -m eleven_trainer build .local/source.json .local/one-serve.json --shots SHOT_ID --phases 1 --interval 3
```

Choose a source serve you have already tested. A name such as “pendulum” does not prove the spin values or recreate the server's motion.

## Build a 10/2 cycle

Replace `ID_A` and `ID_B` with two IDs from the list:

```console
python -m eleven_trainer build .local/source.json .local/cycle.json --shots ID_A ID_B --phases 10 2 --interval 2.8
```

The order is **10 × A, 10 × B, 2 × A, 2 × B**: 24 active rows. It is not 10 A, 2 A, 10 B, 2 B. Add more IDs to extend the sequence. To preserve a deliberately recurring step, list it twice: `--shots ID_A ID_B ID_A`.

Omit `--shots` to use all active source rows in their stored order. A file with 12 exercises can contain 17 distinct rows; those 17 rows produce 204 rows at 10/2. Exercise names do not define grouping. Each selected row is a step.

## Change pacing

Build a new output file with `--interval 3.2` for more time, or a smaller positive value for more frequent launches. This changes the gap between launches, **not the speed of the ball**. It zeroes the interval's random spread, but preserves any source `PostDelay` and all other spread values. Omit `--interval` to preserve all source timing.

If the shot itself is too difficult, adjust and test it in Eleven, then export again. Arbitrarily slowing a ball in JSON can change where it lands. Preserve a known comfortable trajectory while learning the stroke.

## Save and install separate sessions

Use distinct filenames for each drill: `.local/short-backspin.json`, `.local/forehand.json`, `.local/cycle-slower.json`. Existing output files are never overwritten. Inspect and install the file you want, replacing `YOUR_SERIAL`:

```console
python -m eleven_trainer validate .local/one-serve.json
python -m eleven_trainer install .local/one-serve.json --device YOUR_SERIAL
```

Only the selected file is installed. Installation replaces the whole Ball Machine settings file and restarts Eleven; it does not merge with the currently installed library. Previous settings remain in the printed backup location. Keep your source export for building later sessions.
