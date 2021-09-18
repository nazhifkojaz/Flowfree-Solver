using System.Collections.Generic;
using System;
public class BtAlgo
{
  private Board _problem;
  public BtAlgo(Board problem)
  {
    _problem = problem;
  }
  public bool search()
  {
    // best case scenario
    if (_problem.IsAssigned()) return true;
    else
    {
      // iterate through the states
      foreach (var state in _problem.UnassignedStates())
      {
        // iterate through its domain and assign it with a value
        foreach (var candidate in state.Domain)
        {
          state.Value = candidate;
          _problem.NodesCount++;
          // FC.Maintain(_problem);
          // check the validity if it's valid then continue
          if(_problem.IsValid())
          {
            if(search()) return true;
            // search();
          }
          // backtrack one step and assign another value
          // FC.Restore();
          state.Value = -1;
        }
        // for in recursive? bad idea.
        // for (var i = 0; i < state.Domain.Count; i++)
        // {
        //   state.Value = state.Domain[i];
        //   // FC.Maintain(_problem);
        //   if(_problem.IsValid())
        //   {
        //     if(search()) return true;
        //   }
        //   // FC.Restore();
        //   state.Value = -1;
        // }
      }
    }
    return false;
  }
}