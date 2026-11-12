"""On-screen text + station data for 'What TON 618 Would Look Like From Earth at Different Distances' (scene ids k01..k15).
No narrator: only a few short caption lines per station (like the reference film)."""
import math
AU_LY = 63241.077; RS_AU = 1303.0; MOON = 0.5286
def shadow_deg(d_ly):
    r = d_ly * AU_LY / RS_AU
    s = 1.5 * math.sqrt(3) / r * math.sqrt(1 - 1 / r)
    return 2 * math.degrees(math.asin(min(s, 1.0)))

C = lambda *a: list(a)
SCENES = [
 ('k01', None, None, None, None, None, None, None, C(
   "This is TON 618, one of the most massive black holes ever measured.",
   "It is 10.8 billion light-years away. Let's bring it closer.")),
 ('k02', 'THE REAL DISTANCE', '10.8 BILLION LIGHT-YEARS', '10.8 billion light-years', 10.8e9, 3.9 / 3.6e9, '4 millionths of an arcsecond', 'magnitude +15.9 · telescope needed', C(
   "Its light left when the universe was only 3 billion years old.",
   "Estimated mass: 40 to 66 billion Suns. Its shadow is about 4 millionths of an arcsecond wide.",
   "About 10 times smaller than the ring we photographed in Messier 87.")),
 ('k03', 'ONE BILLION LIGHT-YEARS', 'THE LIGHT GROWS', '1 billion light-years', 1e9, None, None, 'magnitude +7.1 · just beyond the naked eye', C(
   "About 3,000 times brighter than at its real distance.",
   "Still a point of light. Distance is what hides it.")),
 ('k04', 'ONE HUNDRED MILLION LIGHT-YEARS', 'FARTHER THAN THE VIRGO CLUSTER', '100 million light-years', 1e8, None, None, 'magnitude +2.1 · like Polaris', C(
   "As bright as Polaris, the North Star. Anyone could see it.",
   "Only a planet-wide network of radio telescopes could begin to resolve its shadow.")),
 ('k05', "ANDROMEDA'S DISTANCE", '2.5 MILLION LIGHT-YEARS', '2.5 million light-years', 2.5e6, None, None, 'magnitude −6.0 · brighter than Venus', C(
   "Brighter than Venus at its best, from the distance of Andromeda.",
   "Andromeda holds about a trillion stars. This single point would outshine them all.")),
 ('k06', 'ACROSS THE MILKY WAY', '100,000 LIGHT-YEARS', '100,000 light-years', 1e5, None, None, 'magnitude −12.9 · like the full Moon', C(
   "The width of our galaxy. As bright as the full Moon.",
   "But all of that light comes from one tiny point.")),
 ('k07', 'THE CENTER OF THE MILKY WAY', '26,000 LIGHT-YEARS', '26,000 light-years', 2.6e4, None, None, 'magnitude −15.9 · 20× the full Moon', C(
   "TON 618 is 15,000 times heavier than the black hole at our galaxy's center.",
   "From here it would shine 20 times brighter than the full Moon.",
   "Its shadow is still smaller than one arcsecond.")),
 ('k08', 'ONE THOUSAND LIGHT-YEARS', 'THE GALACTIC NEIGHBORHOOD', '1,000 light-years', 1e3, None, None, 'magnitude −22.9 · 3% of the Sun', C(
   "Bright enough to cast sharp shadows at night: 3% of the Sun.",
   "Its shadow is a little smaller than Jupiter appears to us.")),
 ('k09', 'ONE HUNDRED LIGHT-YEARS', 'A SECOND SUN', '100 light-years', 1e2, None, None, 'magnitude −27.9 · 3× the Sun', C(
   "3 times brighter than the Sun, mostly as ultraviolet light and X-rays.",
   "No living world could survive in this glare.")),
 ('k10', 'ELEVEN AND A HALF LIGHT-YEARS', 'THE SHADOW EQUALS THE MOON', '11.6 light-years', 11.6, None, None, 'magnitude −32.6 · 225× the Sun', C(
   "The black shadow now covers exactly as much sky as the full Moon.",
   "The glow is gas falling inward, several times wider than the shadow.",
   "225 times brighter than the Sun.")),
 ('k11', "THE NEAREST STAR'S DISTANCE", '4.2 LIGHT-YEARS', '4.2 light-years', 4.24, None, None, 'magnitude −34.8 · 1,700× the Sun', C(
   "The distance to Proxima Centauri. The shadow is almost 3 Moons wide.",
   "Light bends so strongly that a thin bright ring forms at its edge.")),
 ('k12', 'ONE LIGHT-YEAR', "INSIDE THE SUN'S COMET CLOUD", '1 light-year', 1.0, None, None, 'magnitude −37.9 · 30,000× the Sun', C(
   "11 Moons wide and 30,000 times brighter than the Sun.",
   "For the highest mass estimate, its pull is already 16 times the Sun's pull on Earth.")),
 ('k13', 'HALF A LIGHT-YEAR', 'THE SKY IS NO LONGER OURS', '0.5 light-years', 0.5, None, None, 'magnitude −39.4 · 120,000× the Sun', C(
   "23 Moons wide. Its pull is about 66 times the Sun's pull on Earth.",
   "Comets of the Sun's outer cloud would be thrown from their orbits.")),
 ('k14', 'A QUARTER OF A LIGHT-YEAR', 'THE LAST STATION', '0.25 light-years', 0.25, None, None, 'magnitude −41.0 · 480,000× the Sun', C(
   "45 Moons wide, wider than a spread hand at arm's length.",
   "480,000 times brighter than the Sun.",
   "Nothing in our solar system would stay in place.")),
 ('k15', None, None, None, None, None, None, None, C(
   "Now pull back to 10.8 billion light-years.",
   "From here, it is a faint speck: quiet, far away, and harmless.",
   "No one has ever seen its shadow. Every image here is a simulation.")),
]
DUR = {'k01': 30.0, 'k15': 29.0}
for _r in SCENES: DUR.setdefault(_r[0], 37.0)
def cap_times(sid, n):
    """absolute (start, end) seconds for n caption lines; each line stays 6 s with gaps like the reference"""
    T = DUR[sid]
    if sid == 'k01': return [(9.5, 15.5), (18.5, 24.5)][:n]
    if sid == 'k15': return [(2.0, 8.0), (10.5, 16.5), (18.5, 24.5)][:n]
    return {1: [(10.0, 16.0)], 2: [(8.5, 14.5), (19.5, 25.5)], 3: [(7.0, 13.0), (16.0, 22.0), (25.0, 31.0)]}[n]
