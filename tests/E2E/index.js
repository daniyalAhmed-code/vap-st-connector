var newman = require('newman');
const fs = require('fs');
const path = require('path');

// Collection's folder and Report's folder
const collections_folder = path.join(__dirname, './collections/');
const reports_folder = path.join(__dirname, './reports/');

// Get all collection files names from a folder
async function prepareData(folder_path) {
    return new Promise((resolve, reject) => {
        try {
            fs.readdir(folder_path, (err, files) => {
                var collections_files = []

                if (err) { return reject(err); }

                files.forEach(file => {

                    var collection = {
                        collection: {
                            name: file.split('.')[0],
                            file_name: file,
                            path: path.join(folder_path, file)
                        },
                        report: {
                            file_name: file.split('.')[0] + ".report.xml",
                            path: path.join(reports_folder, file.split('.')[0] + ".report.xml",)
                        }
                    }
                    collections_files.push(collection);
                    runNewman(collection)
                });
                return resolve(collections_files);
            });
        } catch (error) {
            return reject(error);
        }
    })
}

async function runNewman(data) {
    return new Promise((resolve, reject) => {
        try {
            newman.run({
                collection: require(data.collection.path),
                reporters: [/* 'cli', */ 'junit'],
                reporter: { junit: { export: data.report.path } }
            })
                // on start of run, log to console
                .on('start', function (err, args) {
                    console.log('running collection: ', data.collection.name + '\n');
                })
                // on start of run, log to console
                .on('done', function (err, summary) {
                    if (err || summary.error) {
                        console.error('collection run encountered an error.');
                    }
                    else {
                        console.log('collection run completed.\nReport generated: ' + data.report.path + '\n');
                    }
                });
        } catch (error) {
            return reject(error);
        }
        return resolve(true);
    })
}

async function main() {
    try {
        var isDirectory = fs.lstatSync(collections_folder).isDirectory()
        if (!isDirectory) {
            throw new Error("Could not find collections folder at '" + collections_folder + "'");
        }
    } catch (error) {
        console.log("Could not find folders\n" + error);
        return 1;
    }

    try {
        prepareData(collections_folder).then((collections) => {
            console.log("Data files:");
            collections.forEach((file) => {
                console.log("Collection name: " + file.collection.name);
                console.log("├── Path to collection: " + file.collection.path);
                console.log("└── Report file: " + file.report.path);
                console.log("\n");
            })
            if (collections.length == 0) {
                throw new Error("No files found inside '%s' folder " + collections_folder)
            }
        })
    } catch (error) {
        console.log("Could not prepare data: %s", error);
        return 1
    }
}

main();