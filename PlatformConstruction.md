# Construction of EDK2-based Platforms

## Discussion

When building an EDK2-based platform, a variety of priorities influence the overall platform construction design.  For example:

* Ease of onboarding new platform maintainers
* Usability & operational complexity (developer efficiency)
* Ownership of code and processes
** Patch review workflows & PR gates
* CI workflows and performance
* Maintenance and Servicing (security fixes)
* Customer support
* Confidentiality
* Intellectual Property
* Performance
* ...

Several patterns of construction are in practice or have been proposed:

* Multiple platforms and owners share a Git repository
  * with a single stable branch
  * with several stable branches separating product families and owners
* Multiple Git repos
  * composed using
    * git-aware submodules
    * [EDK2 Pytool](https://github.com/tianocore/edk2-pytool-extensions) ["Ext Dep" Extension](https://github.com/tianocore/edk2-pytool-extensions/blob/master/docs/features/feature_extdep.md)
    * EDK2 multiple workspaces
    * other tools
  * partitioned across
    * ownership boundaries
    * functional boundaries
    * platform families

The single, shared repository is attractive for its simplicity, but may struggle to support a development environment with many component owners that have different policies and workflows. For example, company Foo may have standardized on certain issue tracking and validation tools.  Squeezing them into a shared repo they don't "own" likely results in "drops" - actual development occurs in repos where they can use their company-standard processes & tools, then code is dropped into the shared repo simply for discoverability.  Versioning of cross-component dependencies is either not tracked, or tracked via documentation or proprietary processes.  It may make more sense to consume component code as it really exists, from separate repos, composed via either submodules or side-by-side multiple workspaces.  Submodules have the advantage of git version control of the versions of submodules.  When servicing a shared repo, all development branches and forks must be rebased to pull in the fixes.  In a submodule design, the branches and forks would more simply pull in the updated submodule.  One idea was to use 1 shared repo where the platform-specific bits were isolated via branches, but this still needs sparse checkouts for developer efficiency and rebases for servicing, without addressing the CI performance concern.

## Strengths of the Different Practices

## Repos

### Single Repo

* Simplicity, discoverability
* Bisect for bug isolation

### Multiple Repos

* Ownership of code & processes
* Servicing is more efficient by simply updating a repo/submodule instead of having to rebase many branches/forks
* CI performance (not having to pull unnecessary bits for the platform targeted)
* Developer efficiency (search indexing, TAB complete)
* Confidentiality & intellectual property access

## Composition

### Submodule Composition

* Git natively tracks the versions of all components & dependencies

### Side-by-side Composition

* Versioning of separate repos either does not happen or is tracked via proprietary mechanisms (README ?)

## Partitioning

### Ownership Partitioning

* Different owners can easily enable & enforce different processes for their repo (PR gates, bug tracking)

### Functional Partitioning

* Discoverability

### Platform Family Partitioning

* Confidentiality & intellectual property

## PyPlatforms Experiment

[Project Mu](https://microsoft.github.io/mu/WhatAndWhy/layout/) platforms typically have 1 repo per silicon vendor (intellectual property, confidentiality) that includes several in-support product families (silicon generations).  Core and silicon code code are separate repos composed via submodules, primarily because each is owned by different parties from the product platform owners.
This PyPlatforms Experiment, where the base repo is forked from [edk2-platforms](https://github.com/tianocore/edk2-platforms) instead of being included via submodule to evaluate these different methods of platform construction.
We observed that sharing code from numerous, unrelated platforms:

* Our fork enables us to enforce our own processes and workflows, but servicing is more expensive, as all branches (and sub-forks) require rebasing versus updating a separate repo/submodule
* Complicated search indexing and TAB complete
** These developer efficiency inconveniences might be mitigated via sparse checkout (e.g. Intel's Repo Tool), but that adds the complexity of managing the sparse checkout.
* Caused unnecessary repo bloat, decreasing performance in particular for CI.

### Some Thoughts

* To improve efficiency of servicing, we have a preference for updating submodules versus rebasing all branches and forks (that are a necessity during product development).
** To this end, push shared, common code into separate git repos, for example Platform/Intel/MinPlatformPkg and related, shared Intel tooling.
* We have a preference for faster PR gates and CI so that bugs can be found faster and a larger test matrix can be executed given available pipelines.  This favors the multiple repo design.
* We found that the Galaga Pro 13 failed to build on VS2017 & VS2019.  CI is recommended to ensure platforms build from tip of tree.  Though this needs a way to declare a repo dependencies, and submodules are not currently employed.  Consider expressing platform dependencies via submodules.
