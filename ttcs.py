
from ortools.sat.python import cp_model

def main():
    # Data
    num_nurses = 4 # số y tá
    num_shifts = 3 # số ca làm việc
    num_days = 3 # số ngày

    # Tạo mô hình
    model = cp_model.CpModel()
    
    schedule = {} # Chứa các ca trực của y tá có thể xảy ra theo ngày và theo ca
    for n in range(num_nurses):
        for d in range(num_days):
            for s in range(num_shifts):
                schedule[(n, d, s)] = model.NewBoolVar('shift_n%id%is%i' % (n, d, s))
                # schedule[(n, d, s)] = 1 nếu y tá đi làm vào ngày n và ca s, và 0 nếu ngược lại.

    # Tạo các ràng buộc cho mô hình
    # Xét ĐK : Mỗi ca được chỉ định cho một y tá duy nhất mỗi ngày.
    for d in range(num_days):
        for s in range(num_shifts):
            model.AddExactlyOne(schedule[(n, d, s)] for n in range(num_nurses)) 
            # Tạo ràng buộc : Đối với mỗi ca, tổng số y tá được chỉ định cho ca đó là 1
    
    # Xét ĐK : Mỗi y tá làm việc nhiều nhất một ca mỗi ngày.
    for n in range(num_nurses):
        for d in range(num_days):
            model.AddAtMostOne(schedule[(n, d, s)] for s in range(num_shifts))
            # Tạo ràng buộc : Đối với mỗi y tá, tổng số ca được giao cho y tá đó nhiều nhất là 1 
    
    # Xét ĐK : Mỗi y tá được phân công ít nhất hai ca trong thời gian ba ngày.
    # ĐK thực tế để ĐK xảy ra : nếu tổng số ca chia cho so y tá (Số ca làm việc ít nhất mà y tá có thể nhận) >= số ca tối thiếu của mỗi y tá (=2)
    min_num_shifts = (num_shifts * num_days) // num_nurses
    if num_shifts * num_days % num_nurses == 0:       
        max_num_shifts = min_num_shifts
    else:
        max_num_shifts = min_num_shifts + 1
    for n in range(num_nurses):
        num_shifts_worked = [] # Tổng số ngày làm việc
        for d in range(num_days):
            for s in range(num_shifts):
                num_shifts_worked.append(schedule[(n, d, s)])
        model.Add(min_num_shifts <= sum(num_shifts_worked))
        model.Add(sum(num_shifts_worked) <= max_num_shifts)
        # Tạo ràng buộc : Số ca làm việc của y tá thuộc khoảng [min_num_shifts:min_num_shifts]

    # Gọi trình giải 
    solver = cp_model.CpSolver()
    solver.parameters.linearization_level = 0
    solver.parameters.enumerate_all_solutions = True

    # In ra các giải pháp
    class NursesPartialSolutionPrinter(cp_model.CpSolverSolutionCallback):
        def __init__(self, schedule, num_nurses, num_days, num_shifts,solution_limit):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self._schedule = schedule
            self._num_nurses = num_nurses
            self._num_days = num_days
            self._num_shifts = num_shifts
            self._solution_count = 0
            self._solution_limit = solution_limit

        def on_solution_callback(self):
            self._solution_count += 1
            print('Giai phap thu %i' % self._solution_count)
            for d in range(self._num_days):
                print('Ngay thu %i' % d)
                for n in range(self._num_nurses):
                    is_working = False
                    for s in range(self._num_shifts):
                        if self.Value(self._schedule[(n, d, s)]):
                            is_working = True
                            print('  Y tá %i lam ca %i' % (n, s))
                    if not is_working:
                        print('  Y ta {} khong lam viec'.format(n))
            if self._solution_count >= self._solution_limit:
                self.StopSearch() # Dừng tìm kiếm giải pháp


    solution_limit = 4
    solution_printer = NursesPartialSolutionPrinter(schedule, num_nurses,num_days, num_shifts,solution_limit)
    solver.Solve(model, solution_printer)
if __name__ == '__main__':
    main()