# 1: Open in compatibility mode.
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()

# Start a session
sess = tf.Session()

# Import the graph
saver = tf.train.import_meta_graph("C:/Users/George/scp_folder/graphs/model.ckpt.meta")
saver.restore(sess, "C:/Users/George/scp_folder/graphs/model.ckpt")

# 2: Identify inputs and outputs.
for op in tf.get_default_graph().get_operations():
    print(op.name)

# 3: Export as TF2 Saved Model.
export_dir = "C:\\Users\\George\\scp_folder\\exported_graphs"

tf.saved_model.simple_save(
    sess,
    export_dir,
    inputs={"input": sess.graph.get_tensor_by_name("Model/input_1:0")},
    outputs={"output": sess.graph.get_tensor_by_name("Model/dense_22/BiasAdd:0")}
)
