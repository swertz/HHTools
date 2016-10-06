      SUBROUTINE LOAD_PARAM_CARD(PATH)

      CHARACTER(128) PATH
      CHARACTER(512) MADLOOP_PATH

      INCLUDE 'coupl.inc'
      CALL SETPARA2(PATH)
      CALL SETPARA(PATH)

      MADLOOP_PATH='/nfs/scratch/fynu/swertz/Madgraph/madgraph5/pp_hh_'
     $ //'all_MV_standalone/SubProcesses/MadLoop5_resources/'

      CALL setMadLoopPath(MADLOOP_PATH)
      
      RETURN
      END
