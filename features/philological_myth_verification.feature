@bdd.feature:philological-myth-verification
Feature: Philological Citation and Verbatim Textual Grounding in Myth and Folklore Corpora

  As a philological researcher and verification engine operator,
  I need deterministic quotation and citation verification rules across folklore,
  comparative mythology, and ethnographic field collections (Parker, Propp, Thompson,
  Lévi-Strauss, and d'Huy/Berezkin)
  So that assertions make contact with empirical primary textual witnesses without
  LLM smoothing, translation drift, or ungrounded paraphrase, and without adjudicating
  scientific notation or equations.

  Rules & Standards:
  1. A pre-verification domain glossary review rehearses philological and mythological commitments.
  2. Typographical, author, title, and year alignment is scored on [0, 100].
  3. Strict Publication Gate: PASS (>= 80.0), WARN (55.0 - 79.9), BLOCK (< 55.0 or mismatch).
  4. AST blockquote citations are verified against primary textual witnesses byte-for-byte.

  Background:
    Given an initialized hermetic verification apparatus with offline cache

  # =========================================================================
  # 1. Structural Folktale Morphology — Vladimir Propp (1968)
  # =========================================================================

  Scenario: Canonical resolution and verbatim citation of folktale morphology
    Given a domain glossary review for "Folktale Morphology"
      | Term              | Inferential Commitment                                            |
      | function          | Act of a character defined from point of view of its significance |
      | dramatis personae | Sphere of action distributing characters into roles               |
      | initial situation | Alpha component preceding narrative lack or villainy              |
    And an empirical citation from folktale morphology
      """
      Propp, V. (1968). Morphology of the Folktale. University of Texas Press.
      """
    And the registry record matches
      | Field  | Value                      |
      | title  | Morphology of the Folktale |
      | author | Vladimir Propp             |
      | year   | 1968                       |
      | source | crossref                   |
    When the citation is scored against the registry record
    Then the composite match score is at least 85.0
    And the gate decision is "pass"

  # =========================================================================
  # 2. Ethnographic Field Collection — Arthur C. Parker (1923) Seneca Myths
  # =========================================================================

  Scenario: Verbatim witness matching of Seneca earth-diver sequence
    Given a canonical primary witness text for "Parker 1923"
      """
      Beneath was only a waste of water where lived ducks and water creatures. The birds saw her falling and flew up with joined wings to cushion her descent. The great Snapping Turtle offered his carapace to support her. The creatures dived for earth mud from the deep bottom, and the muskrat brought up a small morsel, which was placed on the turtle's back, where it grew and expanded into Turtle Island.
      """
    And an mdrag blockquote block with coordinate "doc:seneca:p1:earth-diver"
      """
      > The birds saw her falling and flew up with joined wings to cushion her descent.
      > The great Snapping Turtle offered his carapace to support her.
      """
    When the block is verified against the primary witness
    Then the verbatim status is "verbatim_verified"
    And the matched span covers the verified characters

  Scenario: Adversarial motif alteration in myth witness triggers gate block
    Given a canonical primary witness text for "Parker 1923"
      """
      Beneath was only a waste of water where lived ducks and water creatures. The birds saw her falling and flew up with joined wings to cushion her descent. The great Snapping Turtle offered his carapace to support her. The creatures dived for earth mud from the deep bottom, and the muskrat brought up a small morsel, which was placed on the turtle's back, where it grew and expanded into Turtle Island.
      """
    And an mdrag blockquote block with coordinate "doc:seneca:p1:mutated"
      """
      > The creatures dived for earth mud from the deep bottom, and the beaver brought up a small morsel...
      """
    When the block is verified against the primary witness
    Then the verbatim status is "verbatim_mutated"
    And the divergence reason indicates a missing subspan

  # =========================================================================
  # 3. Comparative Motif Classification — Stith Thompson (1936)
  # =========================================================================

  Scenario: Verification of motif index bibliographic identity
    Given a domain glossary review for "Comparative Mythology"
      | Term      | Inferential Commitment                                            |
      | motif     | Smallest element in a tale having power to persist in tradition   |
      | tale type | Independent traditional narrative capable of standing as a whole  |
    And an empirical citation from comparative folklore
      """
      Thompson, S. (1936). Motif-Index of Folk-Literature. Indiana University Press.
      """
    And the registry record matches
      | Field  | Value                          |
      | title  | Motif-Index of Folk-Literature |
      | author | Stith Thompson                 |
      | year   | 1936                           |
      | source | crossref                       |
    When the citation is scored against the registry record
    Then the composite match score is at least 85.0
    And the gate decision is "pass"

  # =========================================================================
  # 4. Comparative Phylomythology — d'Huy & Berezkin (2018)
  # =========================================================================

  Scenario: Exact verbatim match of deep-time folklore distribution claim
    Given a canonical primary witness text for "d'Huy & Berezkin 2018"
      """
      The Cosmic Hunt is one of the most widespread mythological motifs across Eurasia and the Americas. The core plot involves one or more hunters pursuing one or more animals, which are subsequently transformed into stars or constellations.
      """
    And an mdrag blockquote block with coordinate "doc:phylomyth:s1:cosmic-hunt"
      """
      > The Cosmic Hunt is one of the most widespread mythological motifs across Eurasia and the Americas.
      """
    When the block is verified against the primary witness
    Then the verbatim status is "verbatim_verified"
    And the matched span covers the verified characters
