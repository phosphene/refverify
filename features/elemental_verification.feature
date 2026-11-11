@bdd.feature:elemental-verification
Feature: Hypothetico-Axiomatic Reference Verification and Philological Grounding

  As a scientific researcher and verification engine operator,
  I need deterministic, philologically rigorous citation verification rules
  across elemental disciplines (early electricity, geometry, chemistry, geology, and biology)
  So that claims make contact with empirical primary sources without post-rationalization or entity-swapping.

  Rules & Standards:
  1. A pre-verification domain glossary review rehearses inferential commitments.
  2. Typographical, author, title, and year alignment is scored on [0, 100].
  3. Strict Publication Gate: PASS (>= 80.0), WARN (55.0 - 79.9), BLOCK (< 55.0 or mismatch).
  4. Redundant multi-registry resolution ensures no neural hallucination of existence.

  Background:
    Given an initialized hermetic verification apparatus with offline cache

  # =========================================================================
  # 1. Early Electrical Study — Faraday (1832)
  # =========================================================================

  Scenario: Canonical resolution of foundational electrical research
    Given a domain glossary review for "Early Electricity"
      | Term               | Inferential Commitment                                 |
      | lines of induction | Physical curved curves of magnetic force through space |
      | voltaic battery    | Chemical electromotive potential source                |
      | dielectric         | Insulating medium sustaining electrostatic strain      |
    And an empirical citation from early electrical study
      """
      Faraday, M. (1832). Experimental Researches in Electricity. Philosophical Transactions of the Royal Society of London, 122, 125-162.
      """
    And the registry record matches
      | Field  | Value                                  |
      | title  | Experimental researches in electricity |
      | author | Michael Faraday                        |
      | year   | 1832                                   |
      | doi    | 10.1098/rstl.1832.0006                 |
      | source | crossref                               |
    When the citation is scored against the registry record
    Then the composite match score is at least 85.0
    And the gate decision is "pass"

  Scenario: Adversarial entity swap in electrical study is blocked
    Given an empirical citation from early electrical study
      """
      Faraday, M. (1832). Experimental Researches in Electricity.
      """
    And the registry record has been entity-swapped
      | Field  | Value                                   |
      | title  | Researches on the Acoustic Oscillations |
      | author | Chladni, E.                             |
      | year   | 1802                                    |
      | source | crossref                                |
    When the citation is scored against the registry record
    Then the composite match score is below 55.0
    And the gate decision is "block"

  # =========================================================================
  # 2. Geometry & Topology — Riemann (1868)
  # =========================================================================

  Scenario: Invariant coordinate resolution of foundational geometry
    Given a domain glossary review for "Differential Geometry"
      | Term             | Inferential Commitment                                  |
      | manifold         | n-dimensional continuous space with local coordinates   |
      | curvature tensor | Intrinsic measure of non-Euclidean deviation            |
      | metric ds^2      | Quadratic differential form defining invariant distance |
    And an empirical citation from geometry
      """
      Riemann, B. (1868). Ueber die Hypothesen, welche der Geometrie zu Grunde liegen. Abhandlungen der Koeniglichen Gesellschaft der Wissenschaften zu Goettingen, 13, 133-152.
      """
    And the registry record matches
      | Field  | Value                                                       |
      | title  | Ueber die Hypothesen, welche der Geometrie zu Grunde liegen |
      | author | B. Riemann                                                  |
      | year   | 1868                                                        |
      | source | crossref                                                    |
    When the citation is scored against the registry record
    Then the composite match score is 100.0
    And the gate decision is "pass"

  # =========================================================================
  # 3. Foundations of Chemistry — Lavoisier (1789)
  # =========================================================================

  Scenario: Conservation and stoichiometric reconciliation in chemistry
    Given a domain glossary review for "Foundations of Chemistry"
      | Term                 | Inferential Commitment                                    |
      | caloric              | Material substance of heat (historical operational fluid) |
      | oxygen gas           | Respirable part of air; acidifying principle              |
      | conservation of mass | Invariant mass sum between reagents and products          |
    And an empirical citation from chemistry
      """
      Lavoisier, A. (1789). Traite elementaire de chimie. Cuchet, Paris.
      """
    And the registry record matches
      | Field  | Value                        |
      | title  | Traite elementaire de chimie |
      | author | Antoine Lavoisier            |
      | year   | 1789                         |
      | source | crossref                     |
    When the citation is scored against the registry record
    Then the composite match score is at least 85.0
    And the gate decision is "pass"

  # =========================================================================
  # 4. Geology & Stratigraphy — Lyell (1830)
  # =========================================================================

  Scenario: Stratigraphic superposition and temporal anchoring in geology
    Given a domain glossary review for "Geology & Stratigraphy"
      | Term              | Inferential Commitment                                   |
      | uniformitarianism | Present physical processes account for past formations   |
      | strata            | Sedimentary tabular layers deposited sequentially        |
      | superposition     | Upper strata are strictly younger than underlying strata |
    And an empirical citation from geology
      """
      Lyell, C. (1830). Principles of Geology. John Murray, London.
      """
    And the registry record matches
      | Field  | Value                 |
      | title  | Principles of Geology |
      | author | Charles Lyell         |
      | year   | 1830                  |
      | source | crossref              |
    When the citation is scored against the registry record
    Then the composite match score is at least 85.0
    And the gate decision is "pass"

  # =========================================================================
  # 5. Elemental Biology — Mendel (1866)
  # =========================================================================

  Scenario: Particulate genetic inheritance in elemental biology
    Given a domain glossary review for "Elemental Biology"
      | Term               | Inferential Commitment                                  |
      | dominant/recessive | Phenotypic masking of particulate developmental factors |
      | segregation (3:1)  | Discrete probabilistic factor assortment in gametes     |
      | hybrid generation  | F1 and F2 sequential cross-breeding generations         |
    And an empirical citation from elemental biology
      """
      Mendel, G. (1866). Versuche ueber Pflanzen-Hybriden. Verhandlungen des naturforschenden Vereines in Bruenn, 4, 3-47.
      """
    And the registry record matches
      | Field  | Value                            |
      | title  | Versuche ueber Pflanzen-Hybriden |
      | author | Gregor Mendel                    |
      | year   | 1866                             |
      | source | crossref                         |
    When the citation is scored against the registry record
    Then the composite match score is at least 85.0
    And the gate decision is "pass"
