Philosophy of MusicDB
=====================

There are some major rules and guide lines for MusicDB.
Every decision made follows this philosophy.
They define what MusicDB is, and what it isn't.
The order of the rules defines their priority.
The nested list elements highlight some important implications of the philosophy.

#. The file system is always right.

   * Meta data in files have to be considered wrong.
   * The file system must be able to handle file names with Unicode.
   * The user has to care about a proper naming of the files. MusicDB can support the user with naming, but must not bypass the user.
   * The database is just for cache and augmentation.

#. The show must go on.

   * when errors occur, the software has to go back to a save state and ignore the action that causes the error.
   * If one feature is broken, the rest of the software must be able to continue its work.

#. Bugs must be fixable in less than 15 minutes.

   * If the *Show must go on* rule fails, it must be possible to identify and fix the bug in less 15 minutes.
   * Log everything the software does.
   * The code must be easy to read, not sophisticated.

#. The GUI is for presenting the music, not for controlling software.

   * No control/management buttons if not absolutely necessary.
   * The current playing song is the "hero" and in focus of the presentation.
   * No playlist management, only an easy to handle queue.
   * Strict separation between consuming music, and managing music .

#. The user is always right. Software is just a tool under full control of the user.

   * The software must follow the users decision and not question it.
   * AI and other algorithms shall not replace the users action and decision, just give hints and good defaults.
   * Every decision made by AI or other algorithms must be approved or denied by the user.
   * The source music collection of the user shall be considered sacred. Only apply changes if the user explicitly asks for it.

