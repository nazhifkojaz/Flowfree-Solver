using System.Collections.Generic;
using System;
public static class FC
{
  public static List<List<Record>> History = new List<List<Record>>();
  public static void Maintain(Board board)
  {
    List<Record> temp = new List<Record>();
    foreach (var state in board.AssignedStates())
    {
      temp.Add(state.MaintainDomains());
    }
    History.Add(temp);
  }

  public static void Restore()
  {
    var lastMove = History[History.Count-1];

    foreach (var backtracking in lastMove)
    {
      foreach (var affectedPeer in backtracking.AffectedPeers)
      {
        affectedPeer.Domain.Add(backtracking.Value);
      }
    }
    History.RemoveAt(History.Count-1);
  }
}