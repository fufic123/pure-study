// Hardcoded Organic Chemistry course data — 36 topics, mid-progress.
// Each topic: id, name, complexity (1-10), status, prerequisites (ids).
// Status flows: locked -> available -> in_progress -> mastered.

const TOPICS = [
  // Foundations (mastered)
  { id: "atomic",      name: "Atomic Structure",          complexity: 2, status: "mastered",    prereqs: [] },
  { id: "bonds",       name: "Covalent Bonding",          complexity: 3, status: "mastered",    prereqs: ["atomic"] },
  { id: "lewis",       name: "Lewis Structures",          complexity: 3, status: "mastered",    prereqs: ["bonds"] },
  { id: "vsepr",       name: "VSEPR Geometry",            complexity: 4, status: "mastered",    prereqs: ["lewis"] },
  { id: "hybrid",      name: "Orbital Hybridization",     complexity: 5, status: "mastered",    prereqs: ["vsepr"] },
  { id: "polar",       name: "Bond Polarity",             complexity: 3, status: "mastered",    prereqs: ["bonds"] },

  // Hydrocarbons (mostly mastered, some in progress)
  { id: "alkanes",     name: "Alkanes & Nomenclature",    complexity: 4, status: "mastered",    prereqs: ["hybrid"] },
  { id: "isomers",     name: "Structural Isomers",        complexity: 4, status: "mastered",    prereqs: ["alkanes"] },
  { id: "conform",     name: "Conformational Analysis",   complexity: 5, status: "in_progress", prereqs: ["alkanes"] },
  { id: "stereo",      name: "Stereochemistry",           complexity: 7, status: "in_progress", prereqs: ["isomers", "conform"] },
  { id: "chirality",   name: "Chirality & R/S",           complexity: 7, status: "available",   prereqs: ["stereo"] },
  { id: "alkenes",     name: "Alkenes",                   complexity: 5, status: "mastered",    prereqs: ["alkanes"] },
  { id: "alkynes",     name: "Alkynes",                   complexity: 5, status: "available",   prereqs: ["alkenes"] },
  { id: "aromatic",    name: "Aromaticity",               complexity: 6, status: "available",   prereqs: ["alkenes"] },

  // Functional groups (mixed)
  { id: "haloalk",     name: "Alkyl Halides",             complexity: 5, status: "in_progress", prereqs: ["alkanes", "polar"] },
  { id: "alcohols",    name: "Alcohols",                  complexity: 5, status: "available",   prereqs: ["haloalk"] },
  { id: "ethers",      name: "Ethers & Epoxides",         complexity: 5, status: "locked",      prereqs: ["alcohols"] },
  { id: "amines",      name: "Amines",                    complexity: 6, status: "locked",      prereqs: ["alcohols"] },
  { id: "carbonyl",    name: "Carbonyl Group",            complexity: 6, status: "locked",      prereqs: ["alcohols"] },
  { id: "aldket",      name: "Aldehydes & Ketones",       complexity: 6, status: "locked",      prereqs: ["carbonyl"] },
  { id: "carbox",      name: "Carboxylic Acids",          complexity: 6, status: "locked",      prereqs: ["carbonyl"] },
  { id: "esters",      name: "Esters & Amides",           complexity: 6, status: "locked",      prereqs: ["carbox", "amines"] },

  // Reactions (mostly locked, some available)
  { id: "sn1sn2",      name: "SN1 & SN2 Mechanisms",      complexity: 8, status: "available",   prereqs: ["haloalk", "stereo"] },
  { id: "e1e2",        name: "E1 & E2 Eliminations",      complexity: 8, status: "locked",      prereqs: ["sn1sn2"] },
  { id: "addition",    name: "Electrophilic Addition",    complexity: 7, status: "available",   prereqs: ["alkenes"] },
  { id: "radicals",    name: "Free Radical Reactions",    complexity: 6, status: "locked",      prereqs: ["alkanes", "alkenes"] },
  { id: "diels",       name: "Diels–Alder Reaction",      complexity: 8, status: "locked",      prereqs: ["alkenes", "aromatic"] },
  { id: "eas",         name: "Electrophilic Aromatic Sub.", complexity: 8, status: "locked",    prereqs: ["aromatic"] },
  { id: "oxidation",   name: "Oxidation & Reduction",     complexity: 7, status: "locked",      prereqs: ["alcohols", "aldket"] },
  { id: "grignard",    name: "Grignard Reagents",         complexity: 7, status: "locked",      prereqs: ["haloalk", "carbonyl"] },
  { id: "enolates",    name: "Enolate Chemistry",         complexity: 9, status: "locked",      prereqs: ["aldket"] },
  { id: "aldol",       name: "Aldol Condensation",        complexity: 9, status: "locked",      prereqs: ["enolates"] },

  // Spectroscopy & advanced
  { id: "ir",          name: "IR Spectroscopy",           complexity: 5, status: "available",   prereqs: ["carbonyl"] },
  { id: "nmr",         name: "NMR Spectroscopy",          complexity: 7, status: "locked",      prereqs: ["hybrid", "ir"] },
  { id: "mass",        name: "Mass Spectrometry",         complexity: 6, status: "locked",      prereqs: ["ir"] },
  { id: "synthesis",   name: "Multistep Synthesis",       complexity: 10, status: "locked",     prereqs: ["aldol", "diels", "grignard"] },
];

// Pre-supplied explanations per level. For demo purposes only `chirality` has full content;
// others fall back to a generic template.
const EXPLANATIONS = {
  chirality: {
    1: `**Chirality** is the property of a molecule that makes it non-superimposable on its mirror image, like your left and right hands.

A carbon atom is a **chiral center** when it has four different groups attached to it. The two mirror-image forms are called **enantiomers** — they have identical physical properties except for how they rotate plane-polarized light, and they often interact very differently with biological systems.

We label each chiral center as either **R** (rectus, right) or **S** (sinister, left) using the Cahn–Ingold–Prelog priority rules: rank the four substituents by atomic number, point the lowest-priority group away, and trace 1→2→3. Clockwise = R, counter-clockwise = S.`,
    2: `**Chirality** describes molecules whose mirror images cannot be superimposed — a property arising whenever a tetrahedral atom (typically carbon) has four distinct substituents.

Such an atom is a **stereocenter**. A molecule with one stereocenter has two **enantiomers** (R and S); with *n* stereocenters there are up to 2ⁿ stereoisomers, including **diastereomers** (non-mirror-image stereoisomers).

The **CIP priority rules** assign R/S:
1. Rank the four substituents by atomic number (higher = higher priority). Break ties by moving outward.
2. Orient the molecule so the lowest-priority group points away from you.
3. Trace a path through the remaining three in order of decreasing priority.
4. Clockwise → **R**; counter-clockwise → **S**.

Enantiomers share melting point, density, and most NMR/IR data, but rotate plane-polarized light by equal and opposite amounts. A 50:50 mixture is called a **racemate** and is optically inactive.`,
    3: `**Chirality** is a manifestation of broken mirror symmetry at the molecular scale. Formally, a molecule is chiral if and only if its point group lacks an improper rotation axis (Sₙ) — most commonly when no σ plane and no inversion center exist.

The most familiar source is a **stereogenic carbon** with four distinct substituents, but chirality also arises from atropisomerism (restricted rotation, e.g. BINAP), planar chirality (ferrocenes), and helical chirality (helicenes).

**CIP nomenclature** assigns R/S by ranking ligands via a sphere-by-sphere comparison: atomic number, isotope mass, then phantom atom expansion at each branch. Tied paths require digraph traversal — this is where most novice errors occur.

Practical consequences:
- **Pharmacology**: enantiomers can show drastically different bioactivity (thalidomide, ibuprofen, propranolol).
- **Synthesis**: asymmetric catalysis (chiral auxiliaries, chiral Lewis acids, organocatalysts) is the core of modern enantioselective methodology.
- **Analysis**: chiral HPLC, VCD, and ECD distinguish enantiomers; ee% (enantiomeric excess) quantifies optical purity.

Watch for **meso compounds**: a molecule with multiple stereocenters that is achiral overall because it contains an internal mirror plane.`
  },
  sn1sn2: {
    1: `**SN1** and **SN2** are two ways a nucleophile can replace a leaving group on a carbon atom.

**SN2** happens in one concerted step: the nucleophile attacks from the opposite side of the leaving group, and they swap places simultaneously. This causes **inversion of stereochemistry** at the carbon — like an umbrella flipping inside-out. SN2 prefers methyl and primary carbons (less steric hindrance).

**SN1** happens in two steps: first the leaving group departs to form a **carbocation** intermediate, then the nucleophile attacks. Because the carbocation is flat (sp² hybridized), the nucleophile can approach from either side, producing a **racemic mixture**. SN1 prefers tertiary carbons (more stable carbocation).`,
    2: `**SN1** and **SN2** describe two limiting mechanisms for nucleophilic substitution at sp³ carbon.

**SN2** (substitution, nucleophilic, bimolecular) is concerted: a single transition state in which the nucleophile attacks 180° from the leaving group while the C–LG bond breaks. Rate = k[substrate][nucleophile]. Stereochemistry: clean **inversion** (Walden inversion). Favored by:
- Methyl > primary > secondary; tertiary almost never reacts (steric blockade).
- Strong, charged nucleophiles (HO⁻, RO⁻, CN⁻).
- Polar aprotic solvents (DMSO, DMF, acetone) which solvate cations but not anions.

**SN1** (unimolecular) is stepwise: rate-determining ionization to a carbocation, then nucleophile capture. Rate = k[substrate]. Stereochemistry: **racemization** (often partially, with some inversion bias from ion-pair effects). Favored by:
- Tertiary > secondary; primary almost never (unstable cation).
- Weak/neutral nucleophiles (H₂O, ROH).
- Polar protic solvents (water, alcohols) which stabilize the cation through H-bonding.

Adjacent π-systems (allylic, benzylic) accelerate both pathways via resonance stabilization of the transition state or intermediate.`,
    3: `Beyond the textbook SN1/SN2 dichotomy lies a **continuum** of mechanisms governed by lifetime of the cation-like intermediate (Winstein spectrum) and degree of nucleophile-LG bond exchange in the TS.

Key refinements:
- **Borderline secondary substrates** rarely show pure SN1 or SN2 — most exhibit **ion-pair** behavior. Contact ion pairs give predominantly inverted product; solvent-separated ion pairs give racemization. The Hammond postulate places the TS closer to the cation as the LG departs more.
- **Neighboring-group participation** (NGP / anchimeric assistance): a nearby lone pair or π system displaces the LG intramolecularly, producing a bridged cation (e.g. phenonium, bromonium). Stereochemistry shows double inversion → **net retention**, plus rate enhancement.
- **Carbocation rearrangements**: 1,2-hydride and 1,2-alkyl shifts to more stable cations are diagnostic of SN1. Absence of rearrangement is evidence for SN2 or NGP.
- **Solvent and salt effects**: Grunwald–Winstein Y values quantify ionizing power; mY plots distinguish mechanisms. Common-ion rate depression confirms a free cation intermediate.
- **Kinetic isotope effects**: SN2 shows large secondary α-D KIE (~0.95) from sp³→sp² rehybridization in the TS; SN1 shows even larger values (~1.15) because the TS more fully resembles the planar cation.

Mechanistic assignment in practice combines kinetics, stereochemistry, isotope effects, and Hammett ρ values.`
  }
};

const COPILOT_SCRIPTED = {
  chirality: [
    {
      q: "Why does chirality matter in drug design?",
      a: "Great question. Most drug receptors are themselves chiral — they're built from L-amino acids and have a specific 3D shape. So the two enantiomers of a drug fit the receptor differently, like a left hand in a right glove.\n\nThe textbook example is thalidomide: one enantiomer is sedative, the other caused birth defects. Today, the FDA generally requires single-enantiomer drugs (or rigorous justification for racemates). It's why asymmetric synthesis became one of the most important fields in modern chemistry — and it's what won Knowles, Noyori, and Sharpless the 2001 Nobel."
    }
  ],
  sn1sn2: [
    {
      q: "How do I quickly tell SN1 from SN2 on an exam?",
      a: "Three-question checklist:\n\n1. **What's the substrate?** Methyl/1° → SN2 only. 3° → SN1 only. 2° → look at the other clues.\n2. **What's the nucleophile?** Strong/charged (OH⁻, CN⁻, RO⁻) → SN2. Weak/neutral (H₂O, ROH) → SN1.\n3. **What's the solvent?** Polar aprotic (DMSO, acetone) → SN2. Polar protic (water, MeOH) → SN1.\n\nIf two of three point the same way, that's your mechanism. If you see racemization in the product → SN1. Inversion → SN2."
    }
  ]
};

function getExplanation(topicId, level) {
  const lvl = Math.max(1, Math.min(3, level));
  const set = EXPLANATIONS[topicId];
  if (set && set[lvl]) return set[lvl];
  // Generic fallback
  const t = TOPICS.find(x => x.id === topicId);
  const name = t?.name || "this topic";
  if (lvl === 1) {
    return `**${name}** is a foundational concept you'll need to master before moving on. At this level, focus on the *what* — the definition, the key vocabulary, and one or two canonical examples.\n\nThink of it as the first lap. Don't worry about edge cases yet; just build a mental sketch you can refer back to.`;
  }
  if (lvl === 2) {
    return `**${name}** — let's go deeper.\n\nBeyond the basic definition, you should understand:\n- The underlying *mechanism* or *principle* that makes it work\n- How it relates to neighboring topics in the graph\n- The two or three most common variations or special cases\n\nWork through a problem or two before moving on. The pattern recognition matters more than memorizing rules.`;
  }
  return `**${name}** at the expert level.\n\nHere we examine the limiting cases, the historical experiments that established the theory, and the connections to topics outside this course. You should be able to predict outcomes for novel substrates, recognize when standard rules break down, and explain *why* the underlying physics behaves this way — not just *that* it does.\n\nThis is the level a graduate student or instructor would reason at.`;
}

function getCopilotReply(topicId, message) {
  const scripted = COPILOT_SCRIPTED[topicId];
  if (scripted && scripted.length) {
    return scripted[0].a;
  }
  return `That's a good question about ${TOPICS.find(t => t.id === topicId)?.name || "this topic"}.\n\nIn a connected version, I'd run this through the AI tutor with your full study context. For this prototype, I'm showing a placeholder reply — but the typewriter animation, message history, and chat behavior all work exactly as they would in production.`;
}

const ONBOARDING_SCRIPT = [
  {
    role: "ai",
    text: "Hey, I'm Pure. I build a personalized knowledge graph for whatever you want to learn — then I quiz, explain, and unlock topics as you go.\n\nWhat do you want to learn?"
  },
  {
    role: "user",
    text: "I want to get good at organic chemistry — I'm taking it next semester."
  },
  {
    role: "ai",
    text: "Perfect. Organic is one of my favorites — there's a beautiful structure underneath all the arrows.\n\nA quick sense-check: how much chemistry do you already have?"
  },
  {
    role: "user",
    text: "I took general chem last year. I remember Lewis structures and VSEPR but reactions are fuzzy."
  },
  {
    role: "ai",
    text: "That's a great starting point — you've got the bonding fundamentals locked in. We'll mark those as mastered and start from hybridization.\n\nWhat's your goal? Pass a class, MCAT prep, or something else?"
  },
  {
    role: "user",
    text: "Pass the class with an A. Final's in May."
  },
  {
    role: "ai",
    text: "Got it. I'm building you a 36-topic roadmap from atomic structure through multistep synthesis, with stereochemistry and the substitution/elimination mechanisms as priority paths.\n\nReady?",
    done: true,
    cta: "Open my graph"
  }
];

window.OC_DATA = { TOPICS, EXPLANATIONS, COPILOT_SCRIPTED, ONBOARDING_SCRIPT, getExplanation, getCopilotReply };
