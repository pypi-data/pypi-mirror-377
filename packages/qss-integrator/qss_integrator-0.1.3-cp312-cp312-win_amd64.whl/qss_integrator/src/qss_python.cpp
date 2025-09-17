#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <pybind11/functional.h>
#include "qss_integrator.h"

namespace py = pybind11;

// Python wrapper for QssOde
class PyQssOde : public QssOde {
public:
    using OdeFunction = std::function<std::pair<std::vector<double>, std::vector<double>>(double, const std::vector<double>&, bool)>;
    
    PyQssOde(OdeFunction func) : py_func(func) {}
    
    void odefun(double t, const dvec& y, dvec& q, dvec& d, bool corrector = false) override {
        auto result = py_func(t, y, corrector);
        q = result.first;
        d = result.second;
    }
    
private:
    OdeFunction py_func;
};

PYBIND11_MODULE(qss_py, m) {
    m.doc() = "QSS Integrator Python Wrapper";
    
    // Bind QssOde
    py::class_<QssOde>(m, "QssOde");
    
    py::class_<PyQssOde, QssOde>(m, "PyQssOde")
        .def(py::init<PyQssOde::OdeFunction>());
    
    // Bind QssIntegrator
    py::class_<QssIntegrator>(m, "QssIntegrator")
        .def(py::init<>())
        .def("setOde", &QssIntegrator::setOde)
        .def("initialize", &QssIntegrator::initialize)
        .def("setState", &QssIntegrator::setState)
        .def("integrateToTime", &QssIntegrator::integrateToTime)
        .def("integrateOneStep", &QssIntegrator::integrateOneStep)
        
        // Public members
        .def_readwrite("tn", &QssIntegrator::tn)
        .def_readwrite("y", &QssIntegrator::y)
        .def_readwrite("stabilityCheck", &QssIntegrator::stabilityCheck)
        .def_readwrite("itermax", &QssIntegrator::itermax)
        .def_readwrite("epsmin", &QssIntegrator::epsmin)
        .def_readwrite("epsmax", &QssIntegrator::epsmax)
        .def_readwrite("dtmin", &QssIntegrator::dtmin)
        .def_readwrite("dtmax", &QssIntegrator::dtmax)
        .def_readwrite("ymin", &QssIntegrator::ymin)
        .def_readwrite("enforce_ymin", &QssIntegrator::enforce_ymin)
        .def_readwrite("abstol", &QssIntegrator::abstol)
        .def_readonly("rcount", &QssIntegrator::rcount)
        .def_readonly("gcount", &QssIntegrator::gcount);
}