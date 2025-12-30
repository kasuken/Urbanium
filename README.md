# Urbanium

<img width="1024" height="735" alt="Urbanium" src="https://github.com/user-attachments/assets/3beba508-6c27-4b5d-adce-6db7348ef396" />

Urbanium is a deterministic, agent-based city simulation designed to study emergent urban behavior.

It models a city as a set of explicit systems such as economy, geography, and institutions, and a population of constrained citizens whose decisions are bounded, observable, and reproducible.

Urbanium is not a game and not a chatbot city.  
It is a systems-first experiment framework.

---

## Why Urbanium exists

Most so-called “AI city” projects fail for the same reasons:

- Agents improvise instead of obeying constraints
- Outcomes are narrative rather than measurable
- Results cannot be reproduced
- Cost and complexity explode with scale

Urbanium takes the opposite approach:

- The world owns truth
- Agents propose actions and the world validates them
- Decisions are bounded and enumerable
- Metrics matter more than stories

The goal is to explore how macro-level patterns emerge from micro-level rules under controlled conditions.

---

## Core principles

Deterministic by default  
Same seed, same inputs, same outcome

World-first architecture  
Time, economy, geography, and institutions are simulated explicitly

Bounded agents  
Citizens choose among a small, valid set of actions. No free-form text

Explainable behavior  
Every decision can be traced back to state, traits, and constraints

Metrics over narrative  
Employment, rent, mobility, inequality. Not “what the agent felt”

---

## What Urbanium is

- An agent-based simulation engine
- A policy and systems experimentation sandbox
- A framework for studying emergence
- Compatible with rules, utility models, GOAP, or small local language models

## What Urbanium is not

- A digital twin of a real city
- A generative storytelling system
- A social roleplay environment
- A reinforcement learning benchmark

---

## High-level architecture

World Engine  
- Time  
- Geography (graph)  
- Economy  
- Institutions  
- Events  

Agents  
- Traits  
- Needs  
- Skills  
- Resources  
- Decision model  

Metrics and Observers  
- Employment  
- Rent  
- Mobility  
- Inequality  
- Social structure  

The world advances in discrete ticks.

Each tick:
1. World updates exogenous systems
2. Agents receive their local state
3. Agents propose one action
4. World validates and executes
5. Metrics are recorded

---

## Citizens

Citizens are structured agents, not chatbots.

Each citizen has:
- Stable traits and values
- Skills and resources
- Needs that evolve over time
- Social ties
- Role bindings such as job and home
- A bounded decision model

Decision-making can be implemented using:
- Utility functions
- Rule-based logic
- GOAP
- Small local language models used strictly as decision filters

---

## Available actions (v0)

Urbanium v0 limits agents to seven actions:

- WORK_SHIFT
- REST
- EAT
- COMMUTE
- SOCIALIZE
- JOB_SEARCH
- HOUSING_CHANGE

Actions are proposals.  
The world enforces legality, cost, and consequences.

---

## World state

The world state is explicit and versioned.

It includes:
- Time and random number generation
- Spatial graph and districts
- Labor, housing, and goods markets
- Employers and public services
- Environment and events
- Population and households
- Infrastructure and buildings
- Rolling and snapshot metrics

The world state is the single source of truth.

---

## Metrics first

Urbanium tracks measurable outcomes such as:
- Employment rate
- Wage distribution
- Rent index
- Commute time
- Social network clustering
- Inequality (Gini)
- Agent churn and bankruptcy
- Housing pressure

Results are analyzed across multiple runs and random seeds, not single simulations.

---

## Technology choices

Language  
Python (v0)

Agent reasoning  
Rules, utility models, or small local language models via local inference

Graphs  
Adjacency lists or NetworkX

Metrics  
pandas or polars

Visualization  
Optional and read-only

Performance optimizations in Rust or C++ are considered only once the model stabilizes.

---

## Repository structure

urbanium/
engine/        world state, tick loop, validation  
agents/        citizen models and decision logic  
actions/       action definitions and effects  
scenarios/     initial conditions and experiments  
metrics/       observers and aggregations  
ui/            optional visualization  
docs/  
README.md  

---

## Roadmap

v0 – Foundations
- Deterministic world engine
- 100 citizens
- Core actions implemented
- Metrics pipeline
- Single-city scenario

v1 – Scale and experiments
- 1k or more agents
- Policy interventions
- Multiple districts
- Batch experiment runner

v2 – Extensions
- Crime and enforcement
- Education and skill progression
- Construction and zoning
- Optional learning agents

---

## Non-goals

Urbanium explicitly avoids:
- Free-form conversational agents
- Narrative-driven outcomes
- Hidden state mutations
- “AI magic” without constraints

---

## Status

Urbanium is an active experimental project.

Expect breaking changes.  
Expect iteration.  
Expect refactoring.

---

## License

MIT (subject to change before v1).

---

## Guiding rule

If you can’t measure it, it doesn’t exist.
