// Copyright AGNTCY Contributors (https://github.com/agntcy)
// SPDX-License-Identifier: Apache-2.0

//! gRPC bindings for pubsub service.
pub(crate) mod proto;

pub use proto::pubsub::v1::Content;
pub use proto::pubsub::v1::Message as ProtoMessage;
pub use proto::pubsub::v1::Name as ProtoName;
pub use proto::pubsub::v1::Publish as ProtoPublish;
pub use proto::pubsub::v1::SessionHeader;
pub use proto::pubsub::v1::SessionMessageType as ProtoSessionMessageType;
pub use proto::pubsub::v1::SessionType as ProtoSessionType;
pub use proto::pubsub::v1::SlimHeader;
pub use proto::pubsub::v1::Subscribe as ProtoSubscribe;
pub use proto::pubsub::v1::Unsubscribe as ProtoUnsubscribe;
pub use proto::pubsub::v1::message::MessageType;
pub use proto::pubsub::v1::message::MessageType::Publish as ProtoPublishType;
pub use proto::pubsub::v1::message::MessageType::Subscribe as ProtoSubscribeType;
pub use proto::pubsub::v1::message::MessageType::Unsubscribe as ProtoUnsubscribeType;
pub use proto::pubsub::v1::pub_sub_service_client::PubSubServiceClient;
pub use proto::pubsub::v1::pub_sub_service_server::PubSubServiceServer;
