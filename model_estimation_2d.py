import scipy.io
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def get_covariance(set, mean):
    covariance = np.zeros((2, 2))
    for i in range(len(set)):
        temp = [[set[i][0], set[i][1]]]
        covariance = covariance + np.matmul(np.array(temp).T, temp)

    mean_temp = [[mean[0], mean[1]]]
    covariance = ((1/len(set)) * covariance) - np.matmul(np.array(mean_temp).T, mean_temp)
    return covariance


def get_ML_pair_boundary(Sa, Sb, Ma, Mb, x, y):
    num_steps = len(x)

    boundary = [[0 for _ in range(num_steps)] for _ in range(num_steps)]

    inv_cov_a = np.linalg.inv(Sa)
    inv_cov_b = np.linalg.inv(Sb)
    mean_a = Ma
    mean_b = Mb

    Q0 = np.subtract(inv_cov_a, inv_cov_b)
    Q1 = 2 * (np.dot(mean_b, inv_cov_b) - np.dot(mean_a, inv_cov_a))
    Q2 = np.dot(np.dot(mean_a, inv_cov_a), mean_a.T) - np.dot(np.dot(mean_b, inv_cov_b), mean_b.T)

    for i in range(num_steps):
        for j in range(num_steps):
            coord = [x[i][j], y[i][j]]
            dist = np.matmul(np.matmul(coord, Q0), np.array(coord).T) + np.matmul(Q1, np.array(coord).T) + Q2
            boundary[i][j] = dist

    return boundary


def get_ML_boundary(x, y, ML_ab, ML_ac, ML_bc):
    num_steps = len(x)

    boundary = [[0 for _ in range(num_steps)] for _ in range(num_steps)]

    for i in range(num_steps):
        for j in range(num_steps):
            if ML_ab[i][j] >= 0 and ML_bc[i][j] <= 0:
                boundary[i][j] = 2
            elif ML_bc[i][j] >= 0 and ML_ac[i][j] >= 0:
                boundary[i][j] = 3
            elif ML_ac[i][j] <= 0 and ML_ab[i][j] <= 0:
                boundary[i][j] = 1

    return boundary


def plot_parametric(boundary, x, y, al, bl, cl):
    plt.title("Section 3: Parametric Estimation")
    plt.ylabel("Feature 2")
    plt.xlabel("Feature 1")
    plt.grid(True)

    plt.scatter(al[:, 0], al[:, 1], color='r')
    plt.scatter(bl[:, 0], bl[:, 1], color='g')
    plt.scatter(cl[:, 0], cl[:, 1], color='b')

    contour = plt.contour(x, y, boundary, colors="purple")

    handles = [Rectangle((0, 0), 1, 1, color='r'), Rectangle((0, 0), 1, 1, color='g'),
               Rectangle((0, 0), 1, 1, color='b'), contour.collections[0]]
    labels = ['Class al', 'Class bl', 'Class cl', 'ML Classifier']

    plt.legend(handles, labels)

    plt.show()


def plot_npe(boundary, x, y, al, bl, cl):
    plt.title("Section 3: Non-Parametric Estimation")
    plt.ylabel("Feature 2")
    plt.xlabel("Feature 1")
    plt.grid(True)

    plt.scatter(al[:, 0], al[:, 1], color='r')
    plt.scatter(bl[:, 0], bl[:, 1], color='g')
    plt.scatter(cl[:, 0], cl[:, 1], color='b')

    contour = plt.contour(x, y, boundary, colors="purple")

    handles = [Rectangle((0, 0), 1, 1, color='r'), Rectangle((0, 0), 1, 1, color='g'),
               Rectangle((0, 0), 1, 1, color='b'), contour.collections[0]]
    labels = ['Class al', 'Class bl', 'Class cl', 'ML (NPE) Classifier']

    plt.legend(handles, labels)

    plt.show()


def get_gaussian(x):
    return (1/(2 * np.pi)) * np.exp((-1/2) * np.sum(x * x, axis=1))


def create_pdf(mesh, set, std, var):
    pdf = []
    for i, val in enumerate(mesh):
        x = (val - set) / std
        prob = 1 / np.size(set) * np.sum(1 / var * get_gaussian(x))
        pdf.append(prob)

    return pdf


data_2d = scipy.io.loadmat('data_files/mat/lab2_2.mat')
al_set = data_2d['al'].astype(float)
bl_set = data_2d['bl'].astype(float)
cl_set = data_2d['cl'].astype(float)

# Parametric Estimation

x_min = min(*al_set[:, 0], *bl_set[:, 0], *cl_set[:, 0]) - 1
x_max = max(*al_set[:, 0], *bl_set[:, 0], *cl_set[:, 0]) + 1
y_min = min(*al_set[:, 1], *bl_set[:, 1], *cl_set[:, 1]) - 1
y_max = max(*al_set[:, 1], *bl_set[:, 1], *cl_set[:, 1]) + 1

x_grid = np.linspace(x_min, x_max, num=400)
y_grid = np.linspace(y_min, y_max, num=400)
x1, y1 = np.meshgrid(x_grid, y_grid)

al_mean = np.array([np.mean(al_set[:, 0]), np.mean(al_set[:, 1])])
bl_mean = np.array([np.mean(bl_set[:, 0]), np.mean(bl_set[:, 1])])
cl_mean = np.array([np.mean(cl_set[:, 0]), np.mean(cl_set[:, 1])])

al_cov = get_covariance(al_set, al_mean)
bl_cov = get_covariance(bl_set, bl_mean)
cl_cov = get_covariance(cl_set, cl_mean)

ML_ab = get_ML_pair_boundary(al_cov, bl_cov, al_mean, bl_mean.T, x1, y1)
ML_ac = get_ML_pair_boundary(al_cov, cl_cov, al_mean, cl_mean.T, x1, y1)
ML_bc = get_ML_pair_boundary(bl_cov, cl_cov, bl_mean, cl_mean.T, x1, y1)

total_boundary_plot = get_ML_boundary(x1, y1, ML_ab, ML_ac, ML_bc)

# Non-Parametric Estimation

res = 400
x_mesh = x1.reshape(res*res, 1)     # Arranges by column
y_mesh = y1.reshape(res*res, 1)
mesh_points = np.concatenate((x_mesh, y_mesh), axis=1)

std = 20
var = 400

al_pdf = np.array(create_pdf(mesh_points, al_set, std, var))
bl_pdf = np.array(create_pdf(mesh_points, bl_set, std, var))
cl_pdf = np.array(create_pdf(mesh_points, cl_set, std, var))

al_pdf = al_pdf.reshape(res*res, 1)     # Arranges by column
bl_pdf = bl_pdf.reshape(res*res, 1)
cl_pdf = cl_pdf.reshape(res*res, 1)

pdf_arr = np.concatenate((al_pdf, bl_pdf, cl_pdf), axis=1)
pdf_boundary = np.argmax(pdf_arr, axis=1).reshape(res, res)


if __name__ == '__main__':
    plot_parametric(total_boundary_plot, x_grid, y_grid, al_set, bl_set, cl_set)
    plot_npe(pdf_boundary, x_grid, y_grid, al_set, bl_set, cl_set)