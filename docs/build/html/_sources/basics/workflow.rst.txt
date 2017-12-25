Workflow for development
========================

This section of the documentation describes how to develop MusicDB

Working on code
---------------

All behavior changing changes must be documented in detail in the changlog-documentation.
For each version exists a section, for each module a subsection where the changes are documented, including links to the documentation of the changed method.
Changes should also be mentioned in the method documentation itself.

Only change code in the *develop* branch of the repository.

Please read the :doc:`/basics/concept` chapter and keep them in mind when writing code and adding features.

Rebuilding the Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Do not commit the build directory of the docs until it is really meaningful.
Usually building the documentation is only necessary for a new release.
When developing code, you usually read and edit the docs in the source code.
There may be special cases where rebuilding the documentation can be a good idea.
For example when finishing a new feature.
Then commit the whole build directory.

Using git
---------

The proposed strategy is inspired by `"A successful Git branching model" by Vincent Driessen <http://nvie.com/posts/a-successful-git-branching-model/>`_.
For a project like this, the branching strategy looks like an overkill.
This is why I reduce the concept to the two basic branches *master* and *develop* as well as the *hotfix* branch.
There will be no *release* or *$FEATURE* branch.

In the repository, there are at least the following branches:

   origin/*master*:
      This is the release branch, always containing a stable version of MusicDB, ready to install and run.

   origin/*develop*:
      All development will take place in the this branch.
      It should be in a state that the code will run and will not break anything.
      It is OK and should be considered that there are new features with an unstable interfaces.
      You should *not* run the ``install.sh`` script when you are in the *develop* branch.
      This branch is for integration of new features and bugfixes

   local/*hotfix-$HOTFIX*:
      This is for hotfixes.
      It gets branched from *master* and merged into *master* and *develop*.

When the *develop* branch reaches a stable point, it gets merged to *master*, and a new release tag gets set.

Micro Commits
^^^^^^^^^^^^^

Do use *micro commits*.
So, each bugfix and improvement should be committed independently.

   **Wrong** commit:
      
      * Fixes two bugs, improves the documentation of feature X and optimizes feature Y

   **Correct** commit:
      
      * Fixes bug #42 by implementing the TOA
      * Fixes bug #23 - it was a typo in a variable name
      * Improves the documentation of feature X by adding a ToC
      * Optimizes feature Y by using algorithm Z

With micro commits, a one-line commit messages is usually enough.
Write in this message what the commit does,
and to what feature of bug it is related to.



Createing a Hotfix
^^^^^^^^^^^^^^^^^^
Hotfix branch names always start with ``hotfix-``.

.. code-block:: bash

   git checkout -b hotfix-$HOTFIX master

Before merging the hotfix branch to *master*, make sure everything described in `Releasing a New Version`_ is done.
The *hotfix* branch must also be merged into *develop* to not loose the bugfix.

.. code-block:: bash

   # release the hotfix
   git checkout master                 # go into the master branch
   git merge --no-ff hotfix-$HOTFIX    # merge the hotfix into master
   git tag -a "v$major.$minor.$patch"  # tag with the new patchlevel number

   # merge into the develop branch
   git checkout develop
   git merge --no-ff hotfix-$HOTFIX    # merge the hotfix into master

   git push origin

Merging Develop to Master
^^^^^^^^^^^^^^^^^^^^^^^^^

Before merging the *develop* branch to *master*, make sure everything described in `Releasing a New Version`_ is done.
This will be done in the *develop* branch.
There is no need for an extra *release* branch.

.. code-block:: bash

   git checkout master           # go into the master branch
   git merge --no-ff develop     # merge develop into the master branch
   git tag -a "v$major.$minor.$patch"  # tag with version number


Releasing a New Version
-----------------------

The following things need to be updated for a new release:

   * CHANGELOG file must be up to date
   * docs/source/conf.py: update ``version`` and ``release`` variable
   * musicdb: update ``VERSION`` variable
   * merge branch to master
   * build the new documentation

Further more, the *develop* and *master* branch must be merged and tagged when it is not just a bugfix.

The version number is defined as ``$major.$minor.$patch``.
Tags follow the scheme ``"v$major.$minor.$patch"``.

