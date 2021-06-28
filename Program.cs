using System;
using System.Collections.Generic;

namespace cspNetwork
{
    class Program
    {
        static void Main(string[] args)
        {
            Board newBoard = new Board(6,6, new List<int>{1,2,3,4,5});
            // preassign
            // newBoard.Preassign(new Dictionary<int, int>(){{1, 2}, {8, 2}, {2, 1}, {4, 1}});
            newBoard.Preassign(new Dictionary<int, int>(){{2, 1}, {12, 1}, {8, 3}, {17, 3}, {7, 2}, {28, 2}, {10, 4}, {24, 4}, {25, 5}, {30, 5}});
            // solve
            BtAlgo solver = new BtAlgo(newBoard);
            solver.search();
            newBoard.PrintBoard();
        }
    }
}
