// Copyright AGNTCY Contributors (https://github.com/agntcy)
// SPDX-License-Identifier: Apache-2.0

use std::collections::HashMap;

use pyo3::prelude::*;
use pyo3_stub_gen::derive::gen_stub_pyclass;
use pyo3_stub_gen::derive::gen_stub_pyclass_enum;
use pyo3_stub_gen::derive::gen_stub_pymethods;
use slim_datapath::messages::Name;

use crate::utils::PyName;
use slim_service::FireAndForgetConfiguration;
use slim_service::StreamingConfiguration;
use slim_service::session;
pub use slim_service::session::SESSION_UNSPECIFIED;

#[gen_stub_pyclass]
#[pyclass]
#[derive(Clone)]
pub(crate) struct PySessionInfo {
    pub(crate) session_info: session::Info,
}

impl From<session::Info> for PySessionInfo {
    fn from(session_info: session::Info) -> Self {
        PySessionInfo { session_info }
    }
}

#[gen_stub_pymethods]
#[pymethods]
impl PySessionInfo {
    #[new]
    fn new(session_id: u32) -> Self {
        PySessionInfo {
            session_info: session::Info::new(session_id),
        }
    }

    #[getter]
    fn id(&self) -> u32 {
        self.session_info.id
    }

    #[getter]
    fn source_name(&self) -> PyName {
        let name = match &self.session_info.message_source {
            Some(n) => n.clone(),
            None => Name::from_strings(["", "", ""]),
        };
        PyName::from(name)
    }

    #[getter]
    pub fn destination_name(&self) -> PyName {
        let name = match &self.session_info.message_destination {
            Some(n) => n.clone(),
            None => Name::from_strings(["", "", ""]),
        };
        PyName::from(name)
    }

    #[getter]
    pub fn payload_type(&self) -> String {
        match &self.session_info.payload_type {
            Some(t) => t.clone(),
            None => "".to_string(),
        }
    }

    #[getter]
    pub fn metadata(&self) -> HashMap<String, String> {
        self.session_info.metadata.clone()
    }
}

/// session direction
#[gen_stub_pyclass_enum]
#[pyclass(eq, eq_int)]
#[derive(PartialEq, Clone)]
pub(crate) enum PySessionDirection {
    #[pyo3(name = "SENDER")]
    Sender = session::SessionDirection::Sender as isize,
    #[pyo3(name = "RECEIVER")]
    Receiver = session::SessionDirection::Receiver as isize,
    #[pyo3(name = "BIDIRECTIONAL")]
    Bidirectional = session::SessionDirection::Bidirectional as isize,
}

impl From<PySessionDirection> for session::SessionDirection {
    fn from(value: PySessionDirection) -> Self {
        match value {
            PySessionDirection::Sender => session::SessionDirection::Sender,
            PySessionDirection::Receiver => session::SessionDirection::Receiver,
            PySessionDirection::Bidirectional => session::SessionDirection::Bidirectional,
        }
    }
}

impl From<session::SessionDirection> for PySessionDirection {
    fn from(session_direction: session::SessionDirection) -> Self {
        match session_direction {
            session::SessionDirection::Sender => PySessionDirection::Sender,
            session::SessionDirection::Receiver => PySessionDirection::Receiver,
            session::SessionDirection::Bidirectional => PySessionDirection::Bidirectional,
        }
    }
}

/// session type
#[gen_stub_pyclass_enum]
#[pyclass(eq, eq_int)]
#[derive(PartialEq, Clone)]
pub(crate) enum PySessionType {
    #[pyo3(name = "FIRE_AND_FORGET")]
    FireAndForget = session::SessionType::FireAndForget as isize,
    #[pyo3(name = "STREAMING")]
    Streaming = session::SessionType::Streaming as isize,
}

impl From<PySessionType> for session::SessionType {
    fn from(value: PySessionType) -> Self {
        match value {
            PySessionType::FireAndForget => session::SessionType::FireAndForget,
            PySessionType::Streaming => session::SessionType::Streaming,
        }
    }
}

#[gen_stub_pyclass_enum]
#[derive(Clone, PartialEq)]
#[pyclass(eq)]
pub(crate) enum PySessionConfiguration {
    #[pyo3(constructor = (timeout=None, max_retries=None, sticky=false, mls_enabled=false))]
    FireAndForget {
        timeout: Option<std::time::Duration>,
        max_retries: Option<u32>,
        sticky: bool,
        mls_enabled: bool,
    },

    #[pyo3(constructor = (session_direction, topic, moderator=false, max_retries=0, timeout=std::time::Duration::from_millis(1000), mls_enabled=false))]
    Streaming {
        session_direction: PySessionDirection,
        topic: PyName,
        moderator: bool,
        max_retries: u32,
        timeout: std::time::Duration,
        mls_enabled: bool,
    },
}

impl From<session::SessionConfig> for PySessionConfiguration {
    fn from(session_config: session::SessionConfig) -> Self {
        match session_config {
            session::SessionConfig::FireAndForget(config) => {
                PySessionConfiguration::FireAndForget {
                    timeout: config.timeout,
                    max_retries: config.max_retries,
                    sticky: config.sticky,
                    mls_enabled: config.mls_enabled,
                }
            }
            session::SessionConfig::Streaming(config) => PySessionConfiguration::Streaming {
                session_direction: config.direction.into(),
                topic: config.channel_name.into(),
                moderator: config.moderator,
                max_retries: config.max_retries,
                timeout: config.timeout,
                mls_enabled: config.mls_enabled,
            },
        }
    }
}

impl From<PySessionConfiguration> for session::SessionConfig {
    fn from(value: PySessionConfiguration) -> Self {
        match value {
            PySessionConfiguration::FireAndForget {
                timeout,
                max_retries,
                sticky,
                mls_enabled,
            } => session::SessionConfig::FireAndForget(FireAndForgetConfiguration::new(
                timeout,
                max_retries,
                sticky,
                mls_enabled,
            )),
            PySessionConfiguration::Streaming {
                session_direction,
                topic,
                moderator,
                max_retries,
                timeout,
                mls_enabled,
            } => session::SessionConfig::Streaming(StreamingConfiguration::new(
                session_direction.into(),
                topic.into(),
                moderator,
                Some(max_retries),
                Some(timeout),
                mls_enabled,
            )),
        }
    }
}
