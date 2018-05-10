# This requires retrained_labels.txt and retrained_graph.pb files which are available at this link.
# https://drive.google.com/open?id=1TMCTLEqekAh1zMwdSfWFxMKNKYyfgIYB
# https://drive.google.com/open?id=1d93B2ehbxrpbAhm7OqtvgDT5Mszk4_jc

# Change both file path accordingly.

import tensorflow as tf,sys
import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

print(APP_ROOT)

def function(xyz):
	output = []


	image_path = xyz

	image_data = tf.gfile.FastGFile(image_path,'rb').read()

	label_lines = [line.rstrip() for line
							in tf.gfile.GFile(APP_ROOT + "/tensor/tf_files/retrained_labels.txt")]

	with tf.gfile.FastGFile(APP_ROOT + "/tensor/tf_files/retrained_graph.pb",'rb') as f:
		graph_def = tf.GraphDef()
		graph_def.ParseFromString(f.read())
		_ = tf.import_graph_def(graph_def,name='')

	with tf.Session() as sess:
		softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
		predictions = sess.run(softmax_tensor, \
			{'DecodeJpeg/contents:0': image_data})

		top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]
		i = 0

		for node_id in top_k:
			human_string = label_lines[node_id]
			score = predictions[0][node_id]
			print('%s (score = %.5f)' % (human_string,score))
			output.append(score)
	return output

