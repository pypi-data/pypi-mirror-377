

import argparse




def main():


    parser = argparse.ArgumentParser(description="mypackage CLI")


    parser.add_argument("--output", required=True, help="Output text")


   


    args = parser.parse_args()


    print(args.output)




if __name__ == "__main__":


    main()


