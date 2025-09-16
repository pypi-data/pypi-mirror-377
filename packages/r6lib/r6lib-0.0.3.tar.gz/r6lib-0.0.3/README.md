# r6ops
This is a random operator, loadout and attachment picker for rainbow six siege

## notes
attachments:
  - scopes
      - iron sights: IRON
          - iron sights: IRON
      - non magnifying: NONMAGNIFIED
          - holo a/b/c/d: HOLO_A/B/C/D
          - red dot a/b/c: RED_DOT_A/B/C
          - reflex a/b/c/d: REFLEX_A/B/C/D
      - magnified: MAGNIFIED
          - magnified a/b/c: MAGNIFIED_A/B/C
      - telescopic: TELESCOPIC
          - telescopic a/b: TELESCOPIC_A/B
  - barrels: barrels
      - flash hider: FLASH
      - compensator: COMP
      - muzzle break: MUZZLE
      - suppressor: SUPP
      - extended barrel: EXT
      - none: NONE
  - grips: grips
      - vertical grip: VERT
      - angled grip: ANGLED
      - horizontal grip: HORI
  - under barrel: underbarrels
      - laser: LASER
      - none: NONE
  - gadgets: gadgets
      - attackers: attack
          - breach charge: SOFT
          - claymore: CLAY
          - impact emp grenade: EMP
          - frag grenade: FRAG
          - hard breach: HARD
          - smoke grenade: SMOKE
          - flash grenade: FLASH
      - defenders: defend
          - barbed wire: BARB
          - bulletproof camera: BP
          - deployable shield: DEP
          - observation blocker: OBV
          - impact grenade: IMP
          - c4: CF
          - proximity alarm: PROX
types:
  - operator role types:
      - intel: INTEL
      - anti-gadget: AG
      - support: SUP
      - front line: FL
      - map control: MP
      - breach: BREACH
      - trapper: TRAP
      - anti-entry: AE
      - crowd control: CC
  - weapon types:
      - assault rifle: AR
      - submachine gun: SMG
      - light machine gun: LMG
      - shotgun: SHOTGUN
      - slug shotgun: SLUG
      - precision rifle: RIFLE
      - machine pistol: MP
      - handgun: HG
      - hand cannon: HC
      - shield: SHIELD
operators:
  - sentry: SENTRY
      - ability=! UNIQUE !
  - smoke: SMOKE
      - ability=remote gas grenade: GAS
attributes:
  - weapon attributes: 
      - damage: DAMAGE
      - ads time: ADS
      - fire rate: FIRE_RATE
      - magazine: MAG
      - max capacity: MAX
      - reload speed: RELOAD
      - run speed modifier: RSM
      - destruction: DEST
          - Low: LOW
          - Medium: MED
          - High: HIGH
          - Full: FULL
  - operator attributes:
      - difficulty: difficulty
      - speed: speed
      - health: health
notes:
  - fire rate = 0 means single shot
special options:
  - categorize scopes when randomizing