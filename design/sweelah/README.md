# SweeLah! UI Design and HTML Prototypes

**Status:** Front-end concept / synthetic data only. This does not modify the RetirePilot financial engine or imply pilot readiness.

## Design baseline

**SweeLah! Singapore Playful Neo-Retro.** Mobile-first, flat vector city scenes, colourful Singapore shophouses and Pinnacle@Duxton illustration, warm cream/coral/mint/lavender, rounded typography, tactile cards, Swee the otter, subtle motion and MRT-inspired Life Line. The user-selected v2 layout remains the baseline. The later **Pinnacle floating-clouds** variant changes the front-screen artwork only and keeps the interaction logic.

## Prototypes

| Journey | Original v2 | Latest Pinnacle artwork |
|---|---|---|
| Complete onboarding to dashboard | [HTML](prototypes/SweeLah_Onboarding_and_Dashboard_Prototype.html) | [HTML](prototypes/SweeLah_Onboarding_and_Dashboard_With_Floating_Clouds.html) |
| Onboarding entry | [HTML](prototypes/SweeLah_Onboarding_Prototype.html) | [HTML](prototypes/SweeLah_Onboarding_With_Floating_Clouds.html) |
| Dashboard entry | [HTML](prototypes/SweeLah_Main_Dashboard_Prototype.html) | [HTML](prototypes/SweeLah_Main_Dashboard_With_Floating_Clouds.html) |

The six prototypes are preserved as standalone HTML, with inline styling, scripts and (for floating-clouds variants) embedded animation resources. Download and open in a browser for interactive testing. GitHub's file view shows source; it is not a hosted app.

## Reusable assets

- [Pinnacle city illustration](assets/illustrations/SweeLah_Pinnacle_City_Illustration.png)
- [Pinnacle park illustration](assets/illustrations/SweeLah_Pinnacle_Park_Illustration.png)
- [Floating clouds animated WebP](assets/animation/SweeLah_Pinnacle_Floating_Clouds.webp)
- [Floating clouds still image](assets/illustrations/SweeLah_Pinnacle_Clouds_Still.png)
- [SweeLah initial full UI design](assets/reference/SweeLah_Illustrated_Brand_Concept.png)
- [Pinnacle split-panel reference](assets/reference/SweeLah_Pinnacle_Split_Illustrations.png)
- [Animated family merry-go-round GIF](assets/animation/SweeLah_Merry_Go_Round.gif)

**Animation provenance:** The file previously named `SweeLah_Pinnacle_Floating_Clouds.gif` actually contains a still PNG and is correctly stored as `.png`. The `.webp` file contains the actual floating-cloud animation. The merry-go-round file was supplied with a .png extension but contains a 12-frame animated GIF and is correctly stored as .gif.

## Review previews

See the [screenshots and previews](previews/) and [manifest](ASSET_MANIFEST.json).

## UI information architecture

Onboarding -> Home (financial neighbourhood) -> Life Line (life milestones) -> Ask Swee (guided explanations) -> My Moves (planning checklist). All displayed CPF amounts and balances are synthetic examples. Do not connect real customer financial records to this UI, and do not treat it as a production calculator.

## Accessibility / motion

Keep readable numbers and disclosure text; all button functionality should remain keyboard-accessible. Respect `prefers-reduced-motion`. Use the static PNG illustration as a motion-free fallback. Ensure colours and small text meet applicable contrast requirements before production.

## Handover to Atlas

1. Start with the `With_Floating_Clouds` complete journey for the most recently approved front screen.
2. Preserve original v2 HTMLs as comparison baselines.
3. Extract design tokens and components from the original UI. Do not assume approved financial engine or consent integration.
4. Document visual changes separately; do not silently replace existing app screens.
5. Run responsive, reduced-motion, keyboard and contrast checks before release.

No changes are made to the RetirePilot production security or financial policy by these visual assets.
