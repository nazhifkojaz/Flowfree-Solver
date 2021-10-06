using System.Collections.Generic;
using System;
public class BtAlgo
{
  private Board _problem;
  private List<State> _openList;
  public List<State> OpenList
  {
    get { return _openList; }
    set { _openList = value; }
  }

  public BtAlgo(Board problem)
  {
    _problem = problem;
  }
  // public bool search()
  // {
  //   // best case scenario
  //   if (_problem.IsAssigned()) return true;
  //   else
  //   {
  //     // iterate through the states
  //     foreach (var state in _problem.UnassignedStates())
  //     {
  //       // iterate through its domain and assign it with a value
  //       foreach (var candidate in state.Domain)
  //       {
  //         state.Value = candidate;
  //         _problem.NodesCount++;
  //         // FC.Maintain(_problem);
  //         // check the validity if it's valid then continue
  //         if(_problem.IsValid())
  //         {
  //           if(search()) return true;
  //           // search();
  //         }
  //         // backtrack one step and assign another value
  //         // FC.Restore();
  //         state.Value = -1;
  //       }
  //       // for in recursive? bad idea.
  //       // for (var i = 0; i < state.Domain.Count; i++)
  //       // {
  //       //   state.Value = state.Domain[i];
  //       //   // FC.Maintain(_problem);
  //       //   if(_problem.IsValid())
  //       //   {
  //       //     if(search()) return true;
  //       //   }
  //       //   // FC.Restore();
  //       //   state.Value = -1;
  //       // }
  //     }
  //   }
  //   return false;
  // }


  // in this updated search method, the algorithm search from each preassigned states' head and tail.
  // basically each color (both their heads and tails) are trying to connect to each other
  // this method have (much) smaller B compared to previous method
  public bool search()
  {
    // finished scenario
    if (_problem.IsAssigned()) return true;
    else
    {
      //iterate through active states
      foreach (var current in _problem.GetActiveStates())
      {
        current.Active = false;
        //iterate through current state's unassigned peers
        //this part can also be categorized as 'forward checking', right?
        foreach (var peer in current.GetUnassignedPeers())
        {
          peer.Active = true;
          peer.Value = current.Value;
          _problem.NodesCount++;

          if(_problem.IsValid())
          {
            if(search()) return true;
          }

          peer.Value = -1;
          peer.Active = false;
        }
      }
    }
    return false;
  }
}