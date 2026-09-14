---
title: "Robotic World Models"
summary: "Learned models of environment dynamics, letting a robot anticipate the consequences of an action before committing to it."
image: "/assets/images/research/world-models.jpg"
order: 2
topics:
  - "World Models"
  - "Predictive Modelling"
  - "Model-Based Planning"
# Publications are optional. List BibTeX keys explicitly, and/or match on
# the `keywords` field of entries in _bibliography/papers.bib.
pub_keys: []
pub_keywords:
  - "world-models"
  - "dynamics"
---

Robots that act over long horizons need some model of how the world responds to what
they do. We learn predictive models of environment dynamics that let a robot anticipate
the consequences of an action before committing to it, and use them for planning,
evaluation, and sample-efficient training.

A model that is merely accurate on average is not enough — what matters is whether it is
reliable about the situations where a mistake is expensive.
