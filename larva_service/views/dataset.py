from flask import render_template, redirect, url_for, request, flash, jsonify
from larva_service import app, db
import json
from larva_service.models import remove_mongo_keys
from larva_service.tasks.dataset import calc

@app.route('/dataset', methods=['POST'])
def add_dataset():
    dataset = db.Dataset()
    dataset.name = request.form.get("name")
    dataset.location = request.form.get("location")
    dataset.save()

    calc.delay(unicode(dataset['_id']))

    flash("Dataset created", 'success')
    return redirect(url_for('datasets'))

@app.route('/datasets', methods=['GET'])
@app.route('/datasets.<string:format>', methods=['GET'])
def datasets(format=None):
    if format is None:
        format = 'html'

    datasets = db.Dataset.find()

    if format == 'html':
        return render_template('datasets.html', datasets=datasets)
    elif format == 'json':
        jsond = []
        for ds in datasets:
            js = json.loads(ds.to_json())
            remove_mongo_keys(js)
            js['_id'] = unicode(ds._id)
            jsond.append(js)
        return jsonify( { 'results' : jsond } )
    else:
        flash("Reponse format '%s' not supported" % format)
        return redirect(url_for('datasets'))

@app.route('/datasets/<ObjectId:dataset_id>', methods=['GET'])
@app.route('/datasets/<ObjectId:dataset_id>.<string:format>', methods=['GET'])
def show_dataset(dataset_id, format=None):
    if format is None:
        format = 'html'

    dataset = db.Dataset.find_one( { '_id' : dataset_id } )

    if format == 'html':
        variables = json.dumps(dataset.variables, sort_keys=True, indent=4)
        markers = dataset.google_maps_coordinates()
        return render_template('show_dataset.html', dataset=dataset, markers=markers, variables=variables)
    elif format == 'json':
        jsond = json.loads(dataset.to_json())
        remove_mongo_keys(jsond) #destructive method
        jsond['_id'] = unicode(dataset._id)
        return jsonify( jsond )
    else:
        flash("Reponse format '%s' not supported" % format)
        return redirect(url_for('datasets'))

@app.route('/datasets/<ObjectId:dataset_id>/delete', methods=['GET'])
@app.route('/datasets/<ObjectId:dataset_id>/delete.<string:format>', methods=['GET'])
def delete_dataset(dataset_id, format=None):
    if format is None:
        format = 'html'

    dataset = db.Dataset.find_one( { '_id' : dataset_id } )
    dataset.delete()

    if format == 'json':
        return jsonify( { 'status' : "success" })
    else:
        flash("Dataset deleted")
        return redirect(url_for('datasets'))