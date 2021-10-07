using System;
using System.Collections.Generic;

namespace cspNetwork
{
    class Program
    {
        static void Main(string[] args)
        {
            // parameters -> (board size x, board size y, number of colors)
            // note that boardsize x and y should be the same
            
            // Board newBoard = new Board(5,5, new List<int>{1,2,3,4,5});
            // Board newBoard = new Board(4,4, 2);
            // Board newBoard = new Board(5,5, 4);
            Board newBoard = new Board(5,5,5);
            // Board newBoard = new Board(3,3, 2);
            // Board newBoard = new Board(6,6,6);
            
            
            // preassign
            // newBoard.Preassign(new Dictionary<int, int>(){{1, 2}, {8, 2}, {2, 1}, {4, 1}});
            // newBoard.Preassign(new Dictionary<int, int>(){{1,1}, {31,1}, {2,3}, {14,3}, {8,2}, {26,2}, {20,4}, {32, 4}, {5,5}, {28,5}, {11,6}, {34,6}});
            newBoard.Preassign(new Dictionary<int, int>(){{5, 1}, {8, 1}, {4, 2}, {18, 2}, {6, 3}, {16, 3}, {11, 4}, {21, 4}, {19, 5}, {22, 5}});
            // newBoard.Preassign(new Dictionary<int, int>(){{1, 1}, {9, 1}, {6,2}, {15,2}});
            // newBoard.Preassign(new Dictionary<int, int>(){{0, 1}, {11, 1}, {12,2}, {23,2}, {4,3}, {24,3}});
            // newBoard.Preassign(new Dictionary<int, int>(){{0, 1}, {6, 1}, {4,2}, {5,2}, {8,3}, {15,3}, {13,4}, {16,4}});
            // solve
            BtAlgo solver = new BtAlgo(newBoard);
            // solver.search();
            Console.WriteLine(solver.search());
            Console.WriteLine(newBoard.NodesCount);
            newBoard.PrintBoard();
        }
    }
}
