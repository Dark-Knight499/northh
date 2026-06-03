import sys

from src.functions import core, init, list as list_fn

USAGE = """usage: northh <command> [args]

commands:
  init                    initialize workspace
  idea <text>             capture an idea
  project <name> <text>   create a project entry
  domain <name> <text>    create a domain entry
  journal <text>          create a journal entry
  list                    list everything
  list ideas              list ideas
  list projects           list projects
  list domains            list domains
  list journal            list journal entries
  list project <name>     list entries in a project
  list domain <name>      list entries in a domain
"""


def main():
    if len(sys.argv) < 2:
        from src.ui.app import North

        North().run()
        return

    cmd = sys.argv[1]

    if cmd == "init":
        init.init_workspace()
    elif cmd == "idea":
        if len(sys.argv) < 3:
            print("usage: northh idea <text>")
            return
        core.capture_idea(" ".join(sys.argv[2:]))
    elif cmd == "project":
        if len(sys.argv) < 4:
            print("usage: northh project <name> <text>")
            return
        core.create_project_entry(sys.argv[2], " ".join(sys.argv[3:]))
    elif cmd == "domain":
        if len(sys.argv) < 4:
            print("usage: northh domain <name> <text>")
            return
        core.create_domain_entry(sys.argv[2], " ".join(sys.argv[3:]))
    elif cmd == "journal":
        if len(sys.argv) < 3:
            print("usage: northh journal <text>")
            return
        core.create_journal_entry(" ".join(sys.argv[2:]))
    elif cmd == "list":
        if len(sys.argv) < 3:
            list_fn.ideas()
            list_fn.projects()
            list_fn.domains()
            list_fn.journal()
        elif sys.argv[2] == "ideas":
            list_fn.ideas()
        elif sys.argv[2] == "projects":
            list_fn.projects()
        elif sys.argv[2] == "domains":
            list_fn.domains()
        elif sys.argv[2] == "journal":
            list_fn.journal()
        elif sys.argv[2] == "project":
            if len(sys.argv) < 4:
                print("usage: northh list project <name>")
                return
            list_fn.project(sys.argv[3])
        elif sys.argv[2] == "domain":
            if len(sys.argv) < 4:
                print("usage: northh list domain <name>")
                return
            list_fn.domain(sys.argv[3])
        else:
            print(f"unknown list type: {sys.argv[2]}")
    elif cmd in ("-h", "--help", "help"):
        print(USAGE)
    else:
        print(f"unknown command: {cmd}")
        print(USAGE)


if __name__ == "__main__":
    main()
