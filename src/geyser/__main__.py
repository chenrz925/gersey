from ._internal.argparse import parser
from ._internal.kernel import InteractiveKernel, ScriptKernel


def main():
    args = parser().parse_args()
    if args.args:
        kernel = ScriptKernel(args)
    else:
        kernel = InteractiveKernel(args)

    kernel.run()


if __name__ == '__main__':
    main()
