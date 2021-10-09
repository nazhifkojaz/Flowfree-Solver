using System;
using System.IO;
using System.Linq;
using System.Globalization;
using CsvHelper;
using CsvHelper.Configuration;
using System.Collections.Generic;

namespace cspNetwork
{
    class Program
    {
        static void Main(string[] args)
        {
            // Board newBoard = new Board(5,5, new List<int>{1,2,3,4,5});
            // Board newBoard = new Board(4,4, 2);
            // Board newBoard = new Board(5, 5, 4);
            // Board newBoard = new Board(3,3, new List<int>{1,2});
            // preassign
            // newBoard.Preassign(new Dictionary<int, int>(){{1, 2}, {8, 2}, {2, 1}, {4, 1}});
            // newBoard.Preassign(new Dictionary<int, int>(){{5, 1}, {8, 1}, {4, 2}, {18, 2}, {6, 3}, {16, 3}, {11, 4}, {21, 4}, {19, 5}, {22, 5}});
            // newBoard.Preassign(new Dictionary<int, int>(){{1, 1}, {9, 1}, {6,2}, {15,2}});
            // newBoard.Preassign(new Dictionary<int, int>(){{0, 1}, {11, 1}, {12,2}, {23,2}, {4,3}, {24,3}});
            // newBoard.Preassign(new Dictionary<int, int>() { { 0, 1 }, { 6, 1 }, { 4, 2 }, { 5, 2 }, { 8, 3 }, { 15, 3 }, { 14, 4 }, { 16, 4 } });
            // solve
            // BtAlgo solver = new BtAlgo(newBoard);
            // solver.search();
            // Console.WriteLine(solver.search());
            // Console.WriteLine(newBoard.NodesCount);
            // newBoard.PrintBoard();

            // var records = new List<Data>
            // {
            //   new Data {Index = 1, BoardSize = 5, ColorCount = 2, InitialBoard = "xxx", CompleteBoard = "yyy", ExecutionTime = 123, IsSolvable = true},
            //   new Data {Index = 2, BoardSize = 5, ColorCount = 2, InitialBoard = "xqq", CompleteBoard = "yyy", ExecutionTime = 123, IsSolvable = true},
            //   new Data {Index = 3, BoardSize = 5, ColorCount = 2, InitialBoard = "xqx", CompleteBoard = "yyy", ExecutionTime = 123, IsSolvable = true}
            // };
            // WriteData(records);
            CreateRandomPuzzle(100);

        }
        public static void CreateRandomPuzzle(int n)
        {
          Random rd = new Random();
            Dictionary<string, int> initDict = new Dictionary<string, int>();
            var records = new List<Data>();

            for (int i = 0; i < n; i++)
            {
                int boardSize = rd.Next(5, 9);
                // int boardSize = 5;
                int colorCount = rd.Next(boardSize-2, boardSize+1);
                // int colorCount = 3;

                // create the new board and its data record holder
                var record = new Data { Index = i + 1, BoardSize = boardSize, ColorCount = colorCount };
                var board = new Board(boardSize, boardSize, colorCount);
                List<int> boardStr = Enumerable.Repeat(-1, boardSize*boardSize).ToList();
                
                // generate unique random initial position
                do
                {
                    int colAll = 1;
                    while (colAll <= colorCount)
                    {
                        int colPair = 0;
                        while (colPair < 2)
                        {
                          int idx = rd.Next(boardStr.Count);
                          if(boardStr[idx] == -1)
                          {
                            boardStr[idx] = colAll;
                            colPair++;
                          }
                        }
                        // Console.WriteLine("done one color");
                        colAll++;
                    }
                    // Console.WriteLine("done one board");
                    // Console.WriteLine(initDict.ContainsKey(Stringify(boardStr)));
                    Console.WriteLine("duplicate found");
                } while (initDict.ContainsKey(Stringify(boardStr)));
                // once we create new unique initial pos, then well, copy it
                for (int j = 0; j < boardStr.Count; j++)
                {
                  board.States[j].Value = boardStr[j];
                  if(boardStr[j] != -1) board.States[j].Active = true;
                }
                
                // put initial position to the record holder and dict
                record.InitialBoard = board.GetBoardString();
                initDict.Add(record.InitialBoard, 1);
                
                // solve the board
                BtAlgo solver = new BtAlgo(board);
                record.IsSolvable = solver.search();
                
                // put the execution time and nodes explored
                record.ExecutionTime = 123;
                // record.NodesExplored = 123;
                
                // put final/complete position to record holder
                record.CompleteBoard = board.GetBoardString();
                records.Add(record);
            }
            WriteData(records);
        }
        public static string Stringify(List<int> stateList)
        {
            string str = "";
            foreach (var state in stateList)
            {
                if (state == -1) str += "x";
                else str += state.ToString();
            }
            return str;
        }
        public static void WriteData(List<Data> records)
        {
            var config = new CsvConfiguration(CultureInfo.InvariantCulture) { HasHeaderRecord = false, Delimiter = "," };
            using (var stream = File.Open("record.csv", FileMode.Append))
            using (var writer = new StreamWriter(stream))
            using (var csv = new CsvWriter(writer, config))
            {
                // csv.WriteRecords(records);
                csv.NextRecord();
                foreach (var record in records)
                {
                  csv.WriteRecord(record);
                  csv.NextRecord();
                }
            }
        }

    }
}
