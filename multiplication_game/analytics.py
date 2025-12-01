import pandas as pd
import statistics

class UserProfile:
    def __init__(self, excel_filepath: str):
        self.__excel_filepath = excel_filepath
        try:
            self.__df_focus = pd.read_excel(self.__excel_filepath, sheet_name='Focus Problems',index_col=0,)
            self.__df_performance = pd.read_excel(self.__excel_filepath, sheet_name='Performance')
        except PermissionError as e:
            raise PermissionError(f"Please make sure you don't have the file {self.__excel_filepath} open in another program.  {e}")
        print('Hello World')

    def isQuestionValid(self, a:int, b:int):
        first_permutation_valid = pd.notna(self.__df_focus.at[a,b])
        second_permutation_valid = pd.notna(self.__df_focus.at[b,a])
        return first_permutation_valid | second_permutation_valid
    
    def logQuestionResults(self, question_right:bool, a, b, time_seconds):
        #time_seconds = time_ms/1000
        question_row_index = self.__df_performance[(self.__df_performance['First']==a)&(self.__df_performance['Second']==b)].index[0]
        if pd.isna(self.__df_performance.at[question_row_index,'Times Occurred']):
            self.__df_performance.at[question_row_index,'Times Occurred']=1
            times_answered=0
        else:
            times_answered=int(self.__df_performance.at[question_row_index,'Times Occurred'])
            self.__df_performance.at[question_row_index,'Times Occurred']+=1

        self.__df_performance.at[question_row_index,'Last Time to Answer']=time_seconds
        if question_right:
            if pd.isna(self.__df_performance.at[question_row_index,'Times Right']):
                self.__df_performance.at[question_row_index,'Times Right']=1
            else:
                self.__df_performance.at[question_row_index,'Times Right']+=1
        else:
            if pd.isna(self.__df_performance.at[question_row_index,'Times Wrong']):
                self.__df_performance.at[question_row_index,'Times Wrong']=1
            else:
                self.__df_performance.at[question_row_index,'Times Wrong']+=1
        
        # Establish new average anser time:
        if times_answered==0:
            self.__df_performance.at[question_row_index,'Avg Time to Answer']=time_seconds
        else:
            previous_avg_time = self.__df_performance.at[question_row_index,'Avg Time to Answer']
            previous_answer_durations = [previous_avg_time for i in range(times_answered)]
            total_answer_durations = previous_answer_durations + [time_seconds]
            new_avg = statistics.mean(total_answer_durations)
            self.__df_performance.at[question_row_index,'Avg Time to Answer']=new_avg

    def writePerformanceResultsToFile(self):
        print("Writing Player Session Data to file")
        with pd.ExcelWriter(self.__excel_filepath, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            self.__df_performance.to_excel(writer, sheet_name='Performance', index=False)

    def showResults(self):
        pass
    