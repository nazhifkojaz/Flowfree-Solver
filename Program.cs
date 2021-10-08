using System;
using System.IO;
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
      Board newBoard = new Board(5, 5, 4);
      // Board newBoard = new Board(3,3, new List<int>{1,2});
      // preassign
      // newBoard.Preassign(new Dictionary<int, int>(){{1, 2}, {8, 2}, {2, 1}, {4, 1}});
      // newBoard.Preassign(new Dictionary<int, int>(){{5, 1}, {8, 1}, {4, 2}, {18, 2}, {6, 3}, {16, 3}, {11, 4}, {21, 4}, {19, 5}, {22, 5}});
      // newBoard.Preassign(new Dictionary<int, int>(){{1, 1}, {9, 1}, {6,2}, {15,2}});
      // newBoard.Preassign(new Dictionary<int, int>(){{0, 1}, {11, 1}, {12,2}, {23,2}, {4,3}, {24,3}});
      newBoard.Preassign(new Dictionary<int, int>() { { 0, 1 }, { 6, 1 }, { 4, 2 }, { 5, 2 }, { 8, 3 }, { 15, 3 }, { 14, 4 }, { 16, 4 } });
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

    }
    public static void WriteData(List<Data> records)
    {
      var config = new CsvConfiguration(CultureInfo.InvariantCulture) { HasHeaderRecord = false, Delimiter = "," };
      using (var stream = File.Open("record.csv", FileMode.Append))
      using (var writer = new StreamWriter(stream))
      using (var csv = new CsvWriter(writer, config))
      {
        csv.WriteRecords(records);
        // csv.NextRecord();
        // foreach (var record in records)
        // {
        //   csv.WriteRecord(record);
        //   csv.NextRecord();
        // }
      }
    }

  }
}
