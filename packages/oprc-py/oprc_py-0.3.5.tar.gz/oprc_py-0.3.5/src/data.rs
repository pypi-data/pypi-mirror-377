use crate::telemetry;
use oprc_pb::ObjMeta;
use pyo3::{IntoPyObjectExt, Py, PyAny, PyResult, Python, exceptions::PyRuntimeError};
pub(crate) use zenoh::Session;

use crate::obj::ObjectData;

#[cfg_attr(feature = "stub-gen", pyo3_stub_gen::derive::gen_stub_pyclass)]
#[pyo3::pyclass]
/// Manages data operations for objects, interacting with an object proxy.
pub struct DataManager {
    proxy: oprc_invoke::proxy::ObjectProxy,
}

impl DataManager {
    /// Creates a new `DataManager` instance.
    ///
    /// # Arguments
    ///
    /// * `z_session`: A Zenoh session used for communication.
    pub fn new(z_session: Session) -> Self {
        let proxy = oprc_invoke::proxy::ObjectProxy::new(z_session);
        DataManager { proxy }
    }
}

#[cfg_attr(feature = "stub-gen", pyo3_stub_gen::derive::gen_stub_pymethods)]
#[pyo3::pymethods]
impl DataManager {
    /// Retrieves an object by its class ID, partition ID, and object ID. (Synchronous)
    ///
    /// # Arguments
    ///
    /// * `cls_id`: The class ID of the object.
    /// * `partition_id`: The partition ID where the object resides.
    /// * `obj_id`: The unique ID of the object.
    ///
    /// # Returns
    ///
    /// A `PyResult` containing the Python representation of the object if found,
    /// or `None` if the object does not exist.
    pub fn get_obj(
        &self,
        py: Python<'_>,
        cls_id: String,
        partition_id: u32,
        obj_id: u64,
    ) -> PyResult<Py<PyAny>> {
        let proxy = self.proxy.clone();
        let runtime = pyo3_async_runtimes::tokio::get_runtime();

        let res = py.detach(|| {
            runtime.block_on(async move {
                telemetry::instrument(
                    async move {
                        proxy
                            .get_obj(&ObjMeta {
                                cls_id: cls_id.to_string(),
                                partition_id,
                                object_id: obj_id,
                            })
                            .await
                            .map_err(|e| PyRuntimeError::new_err(e.to_string()))
                    },
                    "data.get_obj",
                )
                .await
            })
        });

        let obj_opt = res?;
        if let Some(obj_val) = obj_opt {
            Ok(ObjectData::from(obj_val).into_py_any(py)?)
        } else {
            Ok(py.None())
        }
    }

    /// Retrieves an object by its class ID, partition ID, and object ID. (Asynchronous)
    ///
    /// # Arguments
    ///
    /// * `cls_id`: The class ID of the object.
    /// * `partition_id`: The partition ID where the object resides.
    /// * `obj_id`: The unique ID of the object.
    ///
    /// # Returns
    ///
    /// A `PyResult` containing the Python representation of the object if found,
    /// or `None` if the object does not exist.
    pub async fn get_obj_async(
        &self,
        cls_id: String,
        partition_id: u32,
        obj_id: u64,
    ) -> PyResult<Py<PyAny>> {
        let proxy = self.proxy.clone();

        let res = telemetry::instrument(
            proxy.get_obj(&ObjMeta {
                cls_id: cls_id.to_string(),
                partition_id,
                object_id: obj_id,
            }),
            "data.get_obj_async",
        )
        .await
        .map_err(|e| PyRuntimeError::new_err(e.to_string()));

        Python::attach(|py| {
            let obj = res?;
            if let Some(obj) = obj {
                Ok(ObjectData::from(obj).into_py_any(py)?)
            } else {
                Ok(py.None())
            }
        })
    }

    /// Sets (creates or updates) an object. (Synchronous)
    ///
    /// # Arguments
    ///
    /// * `obj`: A Python `ObjectData` instance representing the object to be set.
    ///
    /// # Returns
    ///
    /// A `PyResult` indicating success or failure.
    pub fn set_obj(&self, py: Python<'_>, obj: Py<ObjectData>) -> PyResult<()> {
        let proxy = self.proxy.clone();
        let runtime = pyo3_async_runtimes::tokio::get_runtime();

        let proto = {
            let obj_borrowed = obj.borrow(py);
            obj_borrowed.into_proto()
        };

        py.detach(|| {
            runtime.block_on(async move {
                telemetry::instrument(
                    async move {
                        proxy
                            .set_obj(proto)
                            .await
                            .map_err(|e| PyRuntimeError::new_err(e.to_string()))
                    },
                    "data.set_obj",
                )
                .await
            })
        })?;
        Ok(())
    }

    /// Sets (creates or updates) an object. (Asynchronous)
    ///
    /// # Arguments
    ///
    /// * `obj`: A Python `ObjectData` instance representing the object to be set.
    ///
    /// # Returns
    ///
    /// A `PyResult` indicating success or failure.
    pub async fn set_obj_async(&self, obj: Py<ObjectData>) -> PyResult<()> {
        let proto = Python::attach(|py| {
            let obj = obj.borrow(py);
            obj.into_proto()
        });
        telemetry::instrument(self.proxy.set_obj(proto), "data.set_obj_async")
            .await
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
        Ok(())
    }

    /// Deletes an object by its class ID, partition ID, and object ID. (Synchronous)
    ///
    /// # Arguments
    ///
    /// * `cls_id`: The class ID of the object.
    /// * `partition_id`: The partition ID where the object resides.
    /// * `obj_id`: The unique ID of the object.
    ///
    /// # Returns
    ///
    /// A `PyResult` indicating success or failure.
    pub fn del_obj(
        &self,
        py: Python<'_>,
        cls_id: String,
        partition_id: u32,
        obj_id: u64,
    ) -> PyResult<()> {
        let proxy = self.proxy.clone();
        let runtime = pyo3_async_runtimes::tokio::get_runtime();

        py.detach(|| {
            runtime.block_on(async move {
                telemetry::instrument(
                    async move {
                        proxy
                            .del_obj(&ObjMeta {
                                cls_id: cls_id.to_string(),
                                partition_id,
                                object_id: obj_id,
                            })
                            .await
                            .map_err(|e| PyRuntimeError::new_err(e.to_string()))
                    },
                    "data.del_obj",
                )
                .await
            })
        })?;
        Ok(())
    }

    /// Deletes an object by its class ID, partition ID, and object ID. (Asynchronous)
    ///
    /// # Arguments
    ///
    /// * `cls_id`: The class ID of the object.
    /// * `partition_id`: The partition ID where the object resides.
    /// * `obj_id`: The unique ID of the object.
    ///
    /// # Returns
    ///
    /// A `PyResult` indicating success or failure.
    pub async fn del_obj_async(
        &self,
        cls_id: String,
        partition_id: u32,
        obj_id: u64,
    ) -> PyResult<()> {
        telemetry::instrument(
            self.proxy.del_obj(&ObjMeta {
                cls_id: cls_id.to_string(),
                partition_id,
                object_id: obj_id,
            }),
            "data.del_obj_async",
        )
        .await
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
        Ok(())
    }
}
