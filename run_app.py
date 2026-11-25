import sys

if __name__ == '__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--package-self-test':
        from gh3studio.package_check import run
        run(sys.argv[2])
    else:
        from gh3studio.gui import main
        main()
