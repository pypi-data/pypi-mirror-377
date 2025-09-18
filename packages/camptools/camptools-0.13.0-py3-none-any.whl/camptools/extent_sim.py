from argparse import ArgumentParser
from pathlib import Path
import os
import re
import emout

from .utils import call, copy, symlinkdir


def parse_args():
    parser = ArgumentParser()

    parser.add_argument("from_directory")
    parser.add_argument("to_directory", nargs="?", default=None)
    parser.add_argument("--nstep", "-n", type=int, default=None)
    parser.add_argument("--small", "-small", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--submit", "-s", default="mysbatch")
    parser.add_argument("--queue_name", "-qn", default=None)
    parser.add_argument("--afterok", type=int, default=None)

    return parser.parse_args()


def extent_sim():
    args = parse_args()

    from_dir = Path(args.from_directory)
    if not from_dir.exists():
        exit(-1)

    if args.to_directory:
        to_dir = Path(args.to_directory)
    else:
        index = 2
        to_dir = Path(f"{args.from_directory}_{index}")
        while to_dir.exists():
            from_dir = to_dir

            index += 1
            to_dir = Path(f"{args.from_directory}_{index}")

    to_dir.mkdir(exist_ok=True)

    data = emout.Emout(from_dir)
    inp = data.inp

    inp.jobnum[0] = 1
    if args.nstep is not None:
        inp.nstep = args.nstep

    # 最低限の要素の複製を行う場合以下は無視する
    if not args.small:
        copy(from_dir / "job.sh", to_dir / "job.sh")
        copy(from_dir / "mpiemses3D", to_dir / "mpiemses3D")
        copy(from_dir / "generate_xdmf3.py", to_dir / "generate_xdmf3.py")

        for bash in from_dir.glob("*.sh"):
            copy(bash, to_dir)
        for inp_file in from_dir.glob("*.inp"):
            copy(inp_file, to_dir)

    if (from_dir / "plasma.preinp").exists():
        with open(from_dir / "plasma.preinp", "r", encoding="utf-8") as f:
            lines = f.readlines()

        with open(to_dir / "plasma.preinp", "w", encoding="utf-8") as f:
            for line in lines:
                line = re.sub(
                    r"jobnum(\(.*\))? *= *0 *, *[01]", "jobnum(1:2) = 1, 1", line
                )
                if args.nstep:
                    line = re.sub(r"nstep *= *[0-9]+", f"nstep = {args.nstep}", line)
                f.write(line)
    else:
        inp.save(to_dir / "plasma.inp")
    symlinkdir((from_dir / "SNAPSHOT1").resolve(), to_dir / "SNAPSHOT0")

    if args.run:
        os.chdir(to_dir.resolve())

        parts = [args.submit, "job.sh"]

        if args.queue_name:
            parts += ["-qn", args.queue_name]

        if args.afterok:
            parts += ["--afterok", str(args.afterok)]

        cmd = " ".join(parts)

        call(cmd)
