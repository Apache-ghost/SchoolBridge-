const Notice = require('../models/noticeSchema.js');

const noticeCreate = async (req, res) => {
    try {
        const notice = new Notice({
            ...req.body,
            school: req.body.adminID
        })
        const result = await notice.save()

        // 📡 DISTRIBUTED COMMUNICATION: Broadcast notice as event through Communication Service
        try {
            const communicationService = req.app.locals.communicationService;
            
            await communicationService.broadcastEvent(
                req.body.title || 'School Notice',
                req.body.details || req.body.description,
                req.body.date || new Date(),
                req.body.targetAudience || 'school', // school, district, or all
                req.body.priority || 'normal'
            );
            console.log(`📢 Notice broadcast: ${req.body.title || 'School Notice'}`);
        } catch (commError) {
            console.error('⚠️ Failed to broadcast notice via Communication Service:', commError.message);
            // Don't fail the main operation if communication fails
        }

        res.send(result)
    } catch (err) {
        res.status(500).json(err);
    }
};

const noticeList = async (req, res) => {
    try {
        let notices = await Notice.find({ school: req.params.id })
        if (notices.length > 0) {
            res.send(notices)
        } else {
            res.send({ message: "No notices found" });
        }
    } catch (err) {
        res.status(500).json(err);
    }
};

const updateNotice = async (req, res) => {
    try {
        const result = await Notice.findByIdAndUpdate(req.params.id,
            { $set: req.body },
            { new: true })
        res.send(result)
    } catch (error) {
        res.status(500).json(error);
    }
}

const deleteNotice = async (req, res) => {
    try {
        const result = await Notice.findByIdAndDelete(req.params.id)
        res.send(result)
    } catch (error) {
        res.status(500).json(err);
    }
}

const deleteNotices = async (req, res) => {
    try {
        const result = await Notice.deleteMany({ school: req.params.id })
        if (result.deletedCount === 0) {
            res.send({ message: "No notices found to delete" })
        } else {
            res.send(result)
        }
    } catch (error) {
        res.status(500).json(err);
    }
}

module.exports = { noticeCreate, noticeList, updateNotice, deleteNotice, deleteNotices };