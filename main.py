import sys

from src.functions import core, init, list as list_fn, sketch

USAGE = """usage: northh <command> [args] [--voice] [--lang en|hi]

commands:
  init                    initialize workspace
  idea <text>             capture an idea
  idea --voice            capture an idea via speech
  project <name> <text>   create a project entry
  project <name> --voice  create a project entry via speech
  domain <name> <text>    create a domain entry
  domain <name> --voice   create a domain entry via speech
  journal <text>          create a journal entry
  journal --voice         create a journal entry via speech
  list                    list everything
  list ideas              list ideas
  list projects           list projects
  list domains            list domains
  list journal            list journal entries
  list sketches           list sketches
  list project <name>     list entries in a project
  list domain <name>      list entries in a domain
  sketch [name]           open a sketch in the browser (optionally name it)
  sketch <name> -p proj   open a project-specific sketch
  sketch <name> -d dom    open a domain-specific sketch
  sketch <name> -j        open a journal sketch

options:
  --voice                 record via microphone
  --lang en|hi            speech language (default: en)
"""


_LANGUAGES = {"en": "english", "hi": "hindi"}


def _voice_lang():
    for i, a in enumerate(sys.argv):
        if a == "--lang" and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return "en"


def main():
    if len(sys.argv) < 2:
        from src.ui.app import North

        North().run()
        return

    cmd = sys.argv[1]

    if cmd == "init":
        init.init_workspace()
    elif cmd == "idea":
        if "--voice" in sys.argv:
            from src.functions.stt import record_and_transcribe_vad

            lang = _voice_lang()
            print(f"listening... (speak now) [lang={lang}]")
            text = record_and_transcribe_vad(language=lang)
            if text:
                core.capture_idea(text)
                print(f"captured idea: {text}")
            else:
                print("no speech detected")
        elif len(sys.argv) < 3:
            print("usage: northh idea <text>")
            return
        else:
            core.capture_idea(" ".join(sys.argv[2:]))
    elif cmd == "project":
        if "--voice" in sys.argv:
            if len(sys.argv) < 3:
                print("usage: northh project <name> --voice")
                return
            from src.functions.stt import record_and_transcribe_vad

            lang = _voice_lang()
            print(f"listening... (speak now) [lang={lang}]")
            text = record_and_transcribe_vad(language=lang)
            if text:
                core.create_project_entry(sys.argv[2], text)
                print(f"captured project entry: {text}")
            else:
                print("no speech detected")
        elif len(sys.argv) < 4:
            print("usage: northh project <name> <text>")
            return
        else:
            core.create_project_entry(sys.argv[2], " ".join(sys.argv[3:]))
    elif cmd == "domain":
        if "--voice" in sys.argv:
            if len(sys.argv) < 3:
                print("usage: northh domain <name> --voice")
                return
            from src.functions.stt import record_and_transcribe_vad

            lang = _voice_lang()
            print(f"listening... (speak now) [lang={lang}]")
            text = record_and_transcribe_vad(language=lang)
            if text:
                core.create_domain_entry(sys.argv[2], text)
                print(f"captured domain entry: {text}")
            else:
                print("no speech detected")
        elif len(sys.argv) < 4:
            print("usage: northh domain <name> <text>")
            return
        else:
            core.create_domain_entry(sys.argv[2], " ".join(sys.argv[3:]))
    elif cmd == "journal":
        if "--voice" in sys.argv:
            from src.functions.stt import record_and_transcribe_vad

            lang = _voice_lang()
            print(f"listening... (speak now) [lang={lang}]")
            text = record_and_transcribe_vad(language=lang)
            if text:
                core.create_journal_entry(text)
                print(f"captured journal entry: {text}")
            else:
                print("no speech detected")
        elif len(sys.argv) < 3:
            print("usage: northh journal <text>")
            return
        else:
            core.create_journal_entry(" ".join(sys.argv[2:]))
    elif cmd == "list":
        if len(sys.argv) < 3:
            list_fn.ideas()
            list_fn.projects()
            list_fn.domains()
            list_fn.journal()
            list_fn.sketches()
        elif sys.argv[2] == "sketches":
            list_fn.sketches()
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
    elif cmd == "sketch":
        name = ""
        project = ""
        domain = ""
        journal = False
        args = sys.argv[2:]
        i = 0
        while i < len(args):
            if args[i] == "-p" and i + 1 < len(args):
                project = args[i + 1]
                i += 2
            elif args[i] == "-d" and i + 1 < len(args):
                domain = args[i + 1]
                i += 2
            elif args[i] == "-j":
                journal = True
                i += 1
            else:
                name = args[i]
                i += 1

        container_type = None
        container_name = None
        if project:
            container_type = "project"
            container_name = project
        elif domain:
            container_type = "domain"
            container_name = domain
        elif journal:
            container_type = "journal"

        sketch.open_sketch(
            sketch_name=name or None,
            container_type=container_type,
            container_name=container_name,
        )
    elif cmd in ("-h", "--help", "help"):
        print(USAGE)
    else:
        print(f"unknown command: {cmd}")
        print(USAGE)


if __name__ == "__main__":
    main()
