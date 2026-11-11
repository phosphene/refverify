@bdd.feature:verbatim-block-verification
Feature: AST Block-Bounded Verbatim Representation Verification

  As a philological quality-control verifier,
  I need to verify that block-quoted text within Markdown AST blocks
  matches canonical primary source witnesses byte-for-byte (modulo typographic normalization)
  So that upstream LLM smoothing, paraphrasing, and quote hallucination are strictly caught.

  Background:
    Given an initialized hermetic verification apparatus with offline cache

  Scenario: Verbatim quotation in AST block matches witness exactly
    Given a canonical primary witness text for "Faraday 1832"
      """
      By magnetic curves, I mean the lines of magnetic forces, however produced by the magnet
      or the electric current, which would be depicted on surfaces by the use of iron filings;
      or towards which a very small magnetic needle would form a tangent.
      """
    And an mdrag blockquote block with coordinate "doc:faraday:p1:quote1"
      """
      > By magnetic curves, I mean the lines of magnetic forces, however produced by the magnet
      > or the electric current, which would be depicted on surfaces by the use of iron filings...
      """
    When the block is verified against the primary witness
    Then the verbatim status is "verbatim_verified"
    And the matched span covers the verified characters

  Scenario: LLM smoothed quotation in AST block is detected and flagged
    Given a canonical primary witness text for "Faraday 1832"
      """
      By magnetic curves, I mean the lines of magnetic forces, however produced by the magnet
      or the electric current, which would be depicted on surfaces by the use of iron filings.
      """
    And an mdrag blockquote block with coordinate "doc:faraday:p1:quote2"
      """
      > By magnetic curves, I mean the lines of magnetic energy, however produced by the magnet
      > or the electric current.
      """
    When the block is verified against the primary witness
    Then the verbatim status is "verbatim_mutated"
    And the divergence reason indicates a missing subspan
