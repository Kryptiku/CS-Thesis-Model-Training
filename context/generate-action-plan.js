const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, LevelFormat, PageNumber, PageBreak
} = require("docx");

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const cellMargins = { top: 80, bottom: 80, left: 120, right: 120 };

function headerCell(text, width) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: "1B2A4A", type: ShadingType.CLEAR },
    margins: cellMargins,
    children: [new Paragraph({ children: [new TextRun({ text, bold: true, font: "Arial", size: 20, color: "FFFFFF" })] })]
  });
}

function cell(children, width, shading) {
  const opts = {
    borders,
    width: { size: width, type: WidthType.DXA },
    margins: cellMargins,
    children: [new Paragraph({ children })]
  };
  if (shading) opts.shading = { fill: shading, type: ShadingType.CLEAR };
  return new TableCell(opts);
}

function tr(text, opts = {}) {
  return new TextRun({ font: "Arial", size: 22, ...opts, text });
}

function heading(text, level) {
  return new Paragraph({
    heading: level,
    spacing: { before: level === HeadingLevel.HEADING_1 ? 360 : 240, after: 120 },
    children: [new TextRun({ text, font: "Arial", bold: true, size: level === HeadingLevel.HEADING_1 ? 32 : level === HeadingLevel.HEADING_2 ? 26 : 22, color: level === HeadingLevel.HEADING_1 ? "1B2A4A" : "2E5090" })]
  });
}

function para(children, opts = {}) {
  return new Paragraph({ spacing: { after: 120 }, ...opts, children });
}

function bullet(children, ref = "bullets", level = 0) {
  return new Paragraph({ numbering: { reference: ref, level }, spacing: { after: 80 }, children });
}

function numberedItem(children, ref = "numbers", level = 0) {
  return new Paragraph({ numbering: { reference: ref, level }, spacing: { after: 80 }, children });
}

function spacer() {
  return new Paragraph({ spacing: { after: 60 }, children: [] });
}

function divider() {
  return new Paragraph({
    spacing: { before: 200, after: 200 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "CCCCCC", space: 1 } },
    children: []
  });
}

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 360, after: 240 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 240, after: 180 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 22, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 180, after: 120 }, outlineLevel: 2 } },
    ]
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [
        { level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
        { level: 1, format: LevelFormat.BULLET, text: "\u25E6", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 1440, hanging: 360 } } } },
      ]},
      { reference: "numbers", levels: [
        { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
      ]},
      { reference: "numbers2", levels: [
        { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
      ]},
      { reference: "numbers3", levels: [
        { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
      ]},
      { reference: "numbers4", levels: [
        { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
      ]},
      { reference: "numbers5", levels: [
        { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
      ]},
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "1B2A4A", space: 4 } },
          children: [
            tr("CS Thesis: PRNG vs QRNG", { size: 16, color: "666666" }),
            tr("  |  Action Plan", { size: 16, color: "999999" }),
          ]
        })]
      })
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          border: { top: { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC", space: 4 } },
          children: [
            tr("Page ", { size: 16, color: "999999" }),
            new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 16, color: "999999" }),
          ]
        })]
      })
    },
    children: [
      // ===== TITLE =====
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 60 },
        children: [tr("ACTION PLAN", { size: 40, bold: true, color: "1B2A4A" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 60 },
        children: [tr("Finishing Our Thesis", { size: 28, color: "2E5090" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 300 },
        children: [tr("March 28, 2026  |  Defense: April 2026  |  PPO: Done  |  A2C: Done  |  DQN: Pending", { size: 18, color: "666666" })]
      }),

      divider(),

      // ===== WHERE WE ARE =====
      heading("Where We Are Right Now", HeadingLevel.HEADING_1),
      para([
        tr("We" + "\u2019" + "ve completed training and evaluation for "),
        tr("PPO", { bold: true }),
        tr(" and "),
        tr("A2C", { bold: true }),
        tr(". Both show the same result: "),
        tr("no significant difference between PRNG and QRNG", { bold: true, color: "C0392B" }),
        tr(" \u2014 not in maze structure, not in agent performance, not in generalization."),
      ]),
      para([
        tr("This might feel like a failed experiment, but it" + "\u2019" + "s not. Here" + "\u2019" + "s why, and what we need to do to finish strong."),
      ]),

      divider(),

      // ===== WHY NO DIFFERENCE =====
      heading("Why There" + "\u2019" + "s No Difference (The Key Insight)", HeadingLevel.HEADING_1),
      para([
        tr("This is the most important thing for all of us to understand because the panel ", { italics: true }),
        tr("WILL", { bold: true, italics: true }),
        tr(" ask.", { italics: true }),
      ]),

      heading("The Bottleneck Problem", HeadingLevel.HEADING_2),
      para([tr("Our maze generator does this:")]),

      // Flow diagram as a table
      new Table({
        width: { size: 6000, type: WidthType.DXA },
        columnWidths: [6000],
        rows: [
          new TableRow({ children: [new TableCell({
            borders: { top: border, bottom: border, left: border, right: border },
            width: { size: 6000, type: WidthType.DXA },
            shading: { fill: "F5F5F5", type: ShadingType.CLEAR },
            margins: { top: 150, bottom: 150, left: 300, right: 300 },
            children: [
              new Paragraph({ spacing: { after: 60 }, children: [tr("QRNG seed (64-bit integer)", { font: "Courier New", size: 20 })] }),
              new Paragraph({ spacing: { after: 60 }, alignment: AlignmentType.CENTER, children: [tr("\u2193", { size: 20 })] }),
              new Paragraph({ spacing: { after: 60 }, children: [
                tr("random.seed(seed)", { font: "Courier New", size: 20, bold: true }),
                tr("   \u2190 Both paths converge HERE", { size: 20, bold: true, color: "C0392B" })
              ]}),
              new Paragraph({ spacing: { after: 60 }, alignment: AlignmentType.CENTER, children: [tr("\u2193", { size: 20 })] }),
              new Paragraph({ spacing: { after: 60 }, children: [tr("Mersenne Twister engine (Python" + "\u2019" + "s random module)", { font: "Courier New", size: 20 })] }),
              new Paragraph({ spacing: { after: 60 }, alignment: AlignmentType.CENTER, children: [tr("\u2193", { size: 20 })] }),
              new Paragraph({ spacing: { after: 60 }, children: [tr("random.shuffle(4 directions) x ~100 times", { font: "Courier New", size: 20 })] }),
              new Paragraph({ spacing: { after: 60 }, alignment: AlignmentType.CENTER, children: [tr("\u2193", { size: 20 })] }),
              new Paragraph({ children: [tr("20x20 maze output", { font: "Courier New", size: 20 })] }),
            ]
          })] }),
        ]
      }),

      spacer(),
      para([
        tr("The moment we call "),
        tr("random.seed(seed)", { font: "Courier New", size: 20 }),
        tr(", whether the seed came from PRNG or QRNG, "),
        tr("Python" + "\u2019" + "s Mersenne Twister takes over", { bold: true }),
        tr(". From that point, every "),
        tr("random.shuffle()", { font: "Courier New", size: 20 }),
        tr(" call is generated by MT \u2014 the QRNG seed is just a number that initializes MT" + "\u2019" + "s state. MT doesn" + "\u2019" + "t know or care if that number came from a quantum computer or from Python" + "\u2019" + "s random module."),
      ]),

      heading("Why Mersenne Twister is \u201CToo Good\u201D", HeadingLevel.HEADING_2),
      bullet([tr("Period of 2", {}), tr("19937", { superScript: true }), tr(" (will never repeat in our lifetime)")]),
      bullet([tr("623-dimensional equidistribution (statistically uniform in all practical dimensions)")]),
      bullet([tr("Passes all standard randomness tests (Diehard, TestU01, BigCrush)")]),
      spacer(),
      para([
        tr("For the task of shuffling 4 directions ~100 times to carve a 20x20 maze, MT produces output that is "),
        tr("statistically indistinguishable from true randomness", { bold: true }),
        tr(". QRNG" + "\u2019" + "s advantage (true unpredictability) only matters when someone is trying to PREDICT the output (cryptography). We" + "\u2019" + "re not predicting \u2014 we just need uniform shuffles, and MT already gives us that."),
      ]),

      heading("The Algorithm Constraint", HeadingLevel.HEADING_2),
      para([tr("Recursive backtracking on a fixed 20x20 grid is highly constrained:")]),
      bullet([tr("Always produces a perfect maze (spanning tree, one solution path)")]),
      bullet([tr("Fixed number of path cells")]),
      bullet([tr("As carving progresses, fewer valid neighbors remain, so randomness gets funneled into fewer choices")]),
      spacer(),
      para([
        tr("This means the "),
        tr("output space of possible mazes is the same", { bold: true }),
        tr(" regardless of randomness source. Any well-distributed seed source (PRNG or QRNG) maps to the same statistical population of mazes."),
      ]),

      divider(),

      // ===== RESULTS =====
      heading("Our Results Are Actually Strong", HeadingLevel.HEADING_1),

      heading("Null Hypotheses Supported", HeadingLevel.HEADING_2),

      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [3200, 6160],
        rows: [
          new TableRow({ children: [
            headerCell("Hypothesis", 3200),
            headerCell("Evidence", 6160),
          ]}),
          new TableRow({ children: [
            cell([tr("H0-1: No structural difference in mazes", { bold: true, size: 20 })], 3200, "F8F9FA"),
            cell([tr("0/9 metrics significant, all p > 0.05, PERMANOVA p = 0.749, identical medians across 76,800+ mazes per group", { size: 20 })], 6160, "F8F9FA"),
          ]}),
          new TableRow({ children: [
            cell([tr("H0-2: No learning curve difference", { bold: true, size: 20 })], 3200),
            cell([tr("Both PRNG and QRNG agents converge to similar training success rates for both PPO and A2C", { size: 20 })], 6160),
          ]}),
          new TableRow({ children: [
            cell([tr("H0-3: QRNG agents don" + "\u2019" + "t generalize better", { bold: true, size: 20 })], 3200, "F8F9FA"),
            cell([tr("PPO: PRNG agent (78% intra, 76% cross) \u2265 QRNG agent (79% intra, 68% cross). A2C: comparable results", { size: 20 })], 6160, "F8F9FA"),
          ]}),
        ]
      }),

      spacer(),
      heading("Why This Is a Legitimate Contribution", HeadingLevel.HEADING_2),
      bullet([tr("No one has empirically tested this before", { bold: true }), tr(" \u2014 our novelty claim holds")]),
      bullet([tr("We tested across two algorithms", { bold: true }), tr(" (soon three with DQN), 9 structural metrics, and 153,600+ mazes total")]),
      bullet([tr("Proving \u201Cno difference\u201D with rigorous evidence is as valuable as proving a difference")]),
      bullet([tr("We can explain the theoretical WHY \u2014 that" + "\u2019" + "s what makes it strong")]),

      new Paragraph({ children: [new PageBreak()] }),

      // ===== REMAINING TASKS =====
      heading("Remaining Tasks", HeadingLevel.HEADING_1),

      // TASK 1
      heading("Task 1: Run DQN Training + Evaluation (CRITICAL)", HeadingLevel.HEADING_2),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [2000, 7360],
        rows: [
          new TableRow({ children: [
            cell([tr("Who:", { bold: true, size: 20 })], 2000, "FFF3CD"),
            cell([tr("[assign]", { size: 20, color: "C0392B" })], 7360, "FFF3CD"),
          ]}),
          new TableRow({ children: [
            cell([tr("Deadline:", { bold: true, size: 20 })], 2000, "FFF3CD"),
            cell([tr("ASAP (this is the last missing piece)", { size: 20, bold: true, color: "C0392B" })], 7360, "FFF3CD"),
          ]}),
        ]
      }),
      spacer(),
      para([tr("We need DQN to complete our three-algorithm benchmark. Steps:")]),
      numberedItem([tr("Train DQN on PRNG seeds (10M timesteps)")], "numbers"),
      numberedItem([tr("Train DQN on QRNG seeds (10M timesteps)")], "numbers"),
      numberedItem([tr("Run evaluation (4 conditions x 100 episodes)")], "numbers"),
      numberedItem([tr("Run maze metrics extraction")], "numbers"),
      numberedItem([tr("Run statistical analysis")], "numbers"),
      numberedItem([tr("Generate HTML results visualization")], "numbers"),
      spacer(),
      para([
        tr("Expected outcome: ", { bold: true }),
        tr("Same null result as PPO and A2C, which STRENGTHENS our conclusion by showing consistency across three different RL architectures (value-based, actor-critic, policy gradient)."),
      ]),

      // TASK 2
      heading("Task 2: Generate DQN Results Visualization", HeadingLevel.HEADING_2),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [2000, 7360],
        rows: [
          new TableRow({ children: [
            cell([tr("Who:", { bold: true, size: 20 })], 2000, "D4EDDA"),
            cell([tr("[assign]", { size: 20 })], 7360, "D4EDDA"),
          ]}),
          new TableRow({ children: [
            cell([tr("Deadline:", { bold: true, size: 20 })], 2000, "D4EDDA"),
            cell([tr("After DQN training completes", { size: 20 })], 7360, "D4EDDA"),
          ]}),
        ]
      }),
      spacer(),
      para([tr("Same format as our PPO and A2C HTML pages.")]),

      // TASK 3
      heading("Task 3: Write Chapter 4 Discussion", HeadingLevel.HEADING_2),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [2000, 7360],
        rows: [
          new TableRow({ children: [
            cell([tr("Who:", { bold: true, size: 20 })], 2000, "D6EAF8"),
            cell([tr("[assign \u2014 ideally all three collaborate]", { size: 20 })], 7360, "D6EAF8"),
          ]}),
          new TableRow({ children: [
            cell([tr("Deadline:", { bold: true, size: 20 })], 2000, "D6EAF8"),
            cell([tr("Before defense", { size: 20 })], 7360, "D6EAF8"),
          ]}),
        ]
      }),
      spacer(),
      para([tr("The discussion should cover:", { bold: true })]),
      spacer(),

      numberedItem([tr("Summary of findings", { bold: true }), tr(" \u2014 All three algorithms show no significant difference. 0/9 structural metrics differ. Agents perform comparably regardless of seed source.")], "numbers2"),
      numberedItem([tr("The Mersenne Twister bottleneck explanation", { bold: true }), tr(" \u2014 Explain that random.seed() channels all entropy through the same PRNG engine, erasing any distinction between PRNG and QRNG seeds. Cite MT" + "\u2019" + "s properties.")], "numbers2"),
      numberedItem([tr("The algorithmic constraint argument", { bold: true }), tr(" \u2014 Recursive backtracking on a 20x20 grid produces a highly constrained output space.")], "numbers2"),
      numberedItem([tr("What this means for our research questions:", { bold: true })], "numbers2"),

      bullet([tr("RQ1: ", { bold: true }), tr("PRNG and QRNG seeds produce statistically identical maze structures. The generation algorithm acts as an information bottleneck.")], "bullets", 1),
      bullet([tr("RQ2: ", { bold: true }), tr("The source of randomness does not significantly affect learning rate across all three DRL architectures.")], "bullets", 1),
      bullet([tr("RQ3: ", { bold: true }), tr("QRNG-trained agents do not outperform PRNG-trained agents on unseen mazes.")], "bullets", 1),

      numberedItem([tr("Implications:", { bold: true })], "numbers2"),
      bullet([tr("For procedural generation: ", { bold: true }), tr("PRNG (Mersenne Twister) is sufficient. QRNG provides no measurable structural diversity benefit.")], "bullets", 1),
      bullet([tr("For RL training: ", { bold: true }), tr("Agent generalization depends more on algorithm choice (PPO > A2C) and training diversity than on entropy source.")], "bullets", 1),
      bullet([tr("For quantum computing: ", { bold: true }), tr("QRNG" + "\u2019" + "s value lies in contexts requiring unpredictability (cryptography), not uniformity (PCG).")], "bullets", 1),

      numberedItem([tr("Limitations and future work:", { bold: true })], "numbers2"),
      bullet([tr("Bypass MT entirely, using raw quantum random bits at each algorithmic decision point")], "bullets", 1),
      bullet([tr("Test more complex generators (Wave Function Collapse, constraint-based PCG)")], "bullets", 1),
      bullet([tr("Variable maze sizes or 3D environments to expand the output space")], "bullets", 1),
      bullet([tr("Control for seed indexing strategy (144 vs ~3,000 unique mazes seen during training)")], "bullets", 1),

      // TASK 4
      heading("Task 4: Create Combined Results Dashboard (Optional)", HeadingLevel.HEADING_2),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [2000, 7360],
        rows: [
          new TableRow({ children: [
            cell([tr("Who:", { bold: true, size: 20 })], 2000, "E8E8E8"),
            cell([tr("[assign]", { size: 20 })], 7360, "E8E8E8"),
          ]}),
        ]
      }),
      spacer(),
      para([tr("A single HTML page showing PPO vs A2C vs DQN side-by-side, making the \u201Cconsistent null result across architectures\u201D argument visually obvious.")]),

      // TASK 5
      heading("Task 5: Prepare Defense Slides", HeadingLevel.HEADING_2),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [2000, 7360],
        rows: [
          new TableRow({ children: [
            cell([tr("Who:", { bold: true, size: 20 })], 2000, "F0E6FF"),
            cell([tr("All three", { size: 20, bold: true })], 7360, "F0E6FF"),
          ]}),
        ]
      }),
      spacer(),
      para([tr("Key slides:")]),
      numberedItem([tr("Research questions and hypotheses")], "numbers3"),
      numberedItem([tr("Methodology (quick overview)")], "numbers3"),
      numberedItem([tr("Results summary (the consistent null result across all algorithms)")], "numbers3"),
      numberedItem([tr("WHY there" + "\u2019" + "s no difference", { bold: true }), tr(" (the bottleneck diagram \u2014 this is the slide that will impress the panel)")], "numbers3"),
      numberedItem([tr("What this means (PRNG is sufficient, QRNG advantage doesn" + "\u2019" + "t transfer to PCG)")], "numbers3"),
      numberedItem([tr("Future work directions")], "numbers3"),

      new Paragraph({ children: [new PageBreak()] }),

      // ===== PANEL Q&A =====
      heading("How to Handle Panel Questions", HeadingLevel.HEADING_1),

      // Q1
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [9360],
        rows: [new TableRow({ children: [new TableCell({
          borders,
          width: { size: 9360, type: WidthType.DXA },
          shading: { fill: "FFF3CD", type: ShadingType.CLEAR },
          margins: { top: 120, bottom: 120, left: 200, right: 200 },
          children: [
            new Paragraph({ spacing: { after: 80 }, children: [tr("\u201CWhy is there no difference?\u201D", { bold: true, size: 22 })] }),
            new Paragraph({ children: [
              tr("\u2192 ", { color: "2E5090" }),
              tr("The Mersenne Twister bottleneck. Both seed types go through the same PRNG engine. MT is already statistically indistinguishable from true randomness for this application.", { size: 20 }),
            ]}),
          ]
        })] })]
      }),
      spacer(),

      // Q2
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [9360],
        rows: [new TableRow({ children: [new TableCell({
          borders,
          width: { size: 9360, type: WidthType.DXA },
          shading: { fill: "FFF3CD", type: ShadingType.CLEAR },
          margins: { top: 120, bottom: 120, left: 200, right: 200 },
          children: [
            new Paragraph({ spacing: { after: 80 }, children: [tr("\u201CDoesn" + "\u2019" + "t this mean your experiment failed?\u201D", { bold: true, size: 22 })] }),
            new Paragraph({ children: [
              tr("\u2192 ", { color: "2E5090" }),
              tr("No. The experiment successfully answered the research questions. A null result with strong statistical evidence (76,800+ mazes, 9 metrics, 3 algorithms) is a legitimate scientific contribution. We proved that quantum randomness does not provide measurable benefits for DFS-based procedural maze generation.", { size: 20 }),
            ]}),
          ]
        })] })]
      }),
      spacer(),

      // Q3
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [9360],
        rows: [new TableRow({ children: [new TableCell({
          borders,
          width: { size: 9360, type: WidthType.DXA },
          shading: { fill: "FFF3CD", type: ShadingType.CLEAR },
          margins: { top: 120, bottom: 120, left: 200, right: 200 },
          children: [
            new Paragraph({ spacing: { after: 80 }, children: [tr("\u201CWhat would you do differently?\u201D", { bold: true, size: 22 })] }),
            new Paragraph({ children: [
              tr("\u2192 ", { color: "2E5090" }),
              tr("Bypass the Mersenne Twister engine entirely and use raw QRNG bits for each random decision. Use a generation algorithm with less structural constraint and higher entropy sensitivity.", { size: 20 }),
            ]}),
          ]
        })] })]
      }),
      spacer(),

      // Q4
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [9360],
        rows: [new TableRow({ children: [new TableCell({
          borders,
          width: { size: 9360, type: WidthType.DXA },
          shading: { fill: "FFF3CD", type: ShadingType.CLEAR },
          margins: { top: 120, bottom: 120, left: 200, right: 200 },
          children: [
            new Paragraph({ spacing: { after: 80 }, children: [tr("\u201CIs this still novel?\u201D", { bold: true, size: 22 })] }),
            new Paragraph({ children: [
              tr("\u2192 ", { color: "2E5090" }),
              tr("Yes. No prior study has empirically benchmarked QRNG vs PRNG for procedural generation. We are the first to provide quantitative evidence that the theoretical advantages of quantum randomness do not transfer to this domain.", { size: 20 }),
            ]}),
          ]
        })] })]
      }),

      divider(),

      // ===== PRIORITY =====
      heading("Priority Order", HeadingLevel.HEADING_1),

      numberedItem([tr("DQN training", { bold: true }), tr(" (blocks everything else)")], "numbers5"),
      numberedItem([tr("DQN evaluation + visualization", { bold: true })], "numbers5"),
      numberedItem([tr("Chapter 4 discussion writing", { bold: true })], "numbers5"),
      numberedItem([tr("Defense slides", { bold: true })], "numbers5"),
      numberedItem([tr("Combined dashboard", { bold: true }), tr(" (nice to have)")], "numbers5"),
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/Users/angelobaricante/CS-Thesis-Model-Training/context/action-plan.docx", buffer);
  console.log("Done: action-plan.docx created");
});
