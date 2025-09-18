import torch
import photorch.src.stomatal.stomatalmodels as stomat
import time

def getACi(fvcbmtt, gsw, learnrate = 2, maxiteration = 8000, minloss = 1e-10):
    gsmtest = stomat.gsACi(torch.tensor(gsw))
    optimizer = torch.optim.Adam(gsmtest.parameters(), lr=learnrate)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size= 2000, gamma=0.9)
    best_loss = 100000
    best_iter = 0
    best_weights = gsmtest.state_dict()
    criterion = stomat.lossA()
    minloss = minloss
    for iter in range(maxiteration):

        optimizer.zero_grad()
        An_gs = gsmtest()
        fvcbmtt.lcd.Ci = gsmtest.Ci
        fvcbmtt.lcd.A = An_gs
        An_f, Ac_o, Aj_o, Ap_o = fvcbmtt()
        loss = criterion(An_f, An_gs, gsmtest.Ci)

        loss.backward()
        if (iter + 1) % 100 == 0:
            # print(vcmax25)
            print(f'Loss at iter {iter}: {loss.item():.4f}')

        optimizer.step()
        scheduler.step()

        if loss.item() < minloss:
            best_loss = loss.item()
            best_weights = gsmtest.state_dict()
            best_iter = iter
            print(f'Fitting converged at iter {iter}: {loss.item():.4f}')
            break

        if loss.item() < best_loss:
            best_loss = loss.item()
            best_weights = gsmtest.state_dict()
            best_iter = iter
    print(f'Best loss at iter {best_iter}: {best_loss:.4f}')
    gsmtest.load_state_dict(best_weights)
    return gsmtest

class modelresult():
    def __init__(self, stomatalmd_fit, loss_all: torch.tensor, allweights: dict = None):
        self.model = stomatalmd_fit
        self.losses = loss_all
        self.recordweights = allweights

def run(scm, learnrate = 0.5, maxiteration = 20000, minloss = 1e-4, printout = True):
    start_time = time.time()
    optimizer = torch.optim.Adam(scm.parameters(), lr=learnrate)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=5000, gamma=0.9)
    best_loss = 1000000
    best_iter = 0
    best_weights = scm.state_dict()
    criterion = stomat.lossSC()
    loss_all = torch.tensor([])

    for iter in range(maxiteration):

        optimizer.zero_grad()
        gs_fit = scm()
        loss = criterion(scm,gs_fit)
        loss_all =  torch.cat((loss_all, loss.unsqueeze(0)), dim=0)
        loss.backward()
        if (iter + 1) % 200 == 0 and printout:
            # print(vcmax25)
            print(f'Loss at iter {iter}: {loss.item():.4f}')

        optimizer.step()
        scheduler.step()

        if loss.item() < minloss:
            best_loss = loss.item()
            best_weights = scm.state_dict()
            best_iter = iter
            if printout:
                print(f'Fitting converged at iter {iter}: {loss.item():.4f}')
            break

        if loss.item() < best_loss:
            best_loss = loss.item()
            best_weights = scm.state_dict()
            best_iter = iter
    end_time = time.time()
    elapsed_time = end_time - start_time
    if printout:
        print(f'Best loss at iter {best_iter}: {best_loss:.4f}')
        print(f'Fitting time: {elapsed_time:.4f} seconds')
    scm.load_state_dict(best_weights)

    modelresult_out = modelresult(scm, loss_all)
    return modelresult_out