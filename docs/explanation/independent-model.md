# How the independent pack was derived

The initial personal library used existing numerical launch settings. To explore an independent replacement, a fresh agent received the JSON schema and was instructed not to read those files, community packs or their launch parameters. It produced twelve new targets and a ballistic generator. The current package uses that generator and the project's repetition/installation code; it imports no prior trajectory data.

## Geometry and equations

The declared model has a 2.74 m by 1.525 m table, tabletop at y=0.76 m, a net 0.1525 m above it and a ball radius of 0.020 m. Gravity is 9.81 m/s². Its origin is on the floor below the net center, x is the receiver's right, y is up and z points toward the receiver. These are model assumptions, not measurements of the game.

The independently chosen launch point is (0, 1.18, -1.60) metres. Given a target and a chosen apex, the generator solves:

```text
vy = sqrt(2 g (apex_y - launch_y))
T = (vy + sqrt(vy² + 2 g (launch_y - contact_y))) / g
vx = (target_x - launch_x) / T
vz = (target_z - launch_z) / T
speed = sqrt(vx² + vy² + vz²)
horizontal = atan2(vx, vz)
vertical = atan2(vy, sqrt(vx² + vz²))
```

Contact height is tabletop height plus ball radius. Checks account for the ball's radius at table edges and while sweeping across the net plane. A separate review reconstructed velocity from the serialized settings and confirmed the model's target intersections. This validates the calculation, not Eleven's behavior.

## Spin and native mapping

Chosen surface-speed ratios define trial spin magnitudes: `omega = ratio * speed / radius`. Topspin uses +0.18, backspin -0.14, and sidespin ±0.12. The physical ratios are design choices; native spin units, signs and response are unmeasured.

The generator omits air drag, Magnus force and bounce dynamics. Spinning rows therefore have reference landing targets, not spin-aware predictions. They describe direct machine feeds that cross to the receiver before the first table bounce, not a simulation of a legal serve or a server's pendulum motion.

`eleven_trainer/experimental/calibration.json` declares provisional position, angle, speed, spin and timing mappings. Identity position/speed, degree angles and rad/s spin are guesses. A measured mapping can replace them without borrowing another pack's trajectories. Native axis and unit calibration comes before tuning flight and spin effects.

## Reproduce or calibrate

From the repository root:

```console
python -m eleven_trainer.experimental.generate
```

This regenerates the base twelve rows, 42 selectable variants, catalog checksums, diagnostics and model results. For a separate experiment:

```console
python -m eleven_trainer.experimental.generate --calibration .local/measured-calibration.json --output-dir .local/regenerated
```

Generated files from an alternate directory can be used with `validate` and `install`; `trial` continues to use the bundled catalog. No community download is used by generation. Minimum measurement work is to establish position origin/axes/scale, angle conventions, neutral speed behavior, and each spin axis separately, then observe trajectories and bounces in Eleven.
